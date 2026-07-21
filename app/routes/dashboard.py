"""
Dashboard Routes
Handles the main dashboard view with statistics and charts.
"""

from flask import Blueprint, render_template, jsonify
from app.utils.helpers import login_required
from app.models.execution import Execution
from app.models.test_case import TestCase
from app.utils.database import execute_query

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Render the main dashboard."""
    return render_template('dashboard.html')


@dashboard_bp.route('/api/dashboard/stats')
@login_required
def get_stats():
    """API endpoint for dashboard statistics."""
    # Total test cases
    tc_query = "SELECT COUNT(*) as total FROM test_cases"
    tc_result = execute_query(tc_query, fetch_one=True)
    total_cases = tc_result['total'] if tc_result else 0

    # Execution stats
    exec_stats = Execution.get_stats()

    # Priority distribution
    priority_query = """
        SELECT priority, COUNT(*) as count
        FROM test_cases
        GROUP BY priority
    """
    priority_dist = execute_query(priority_query, fetch_all=True) or []

    # Severity distribution
    severity_query = """
        SELECT severity, COUNT(*) as count
        FROM test_cases
        GROUP BY severity
    """
    severity_dist = execute_query(severity_query, fetch_all=True) or []

    return jsonify({
        'total_cases': total_cases,
        'passed': exec_stats['passed'] or 0 if exec_stats else 0,
        'failed': exec_stats['failed'] or 0 if exec_stats else 0,
        'blocked': exec_stats['blocked'] or 0 if exec_stats else 0,
        'not_executed': exec_stats.get('not_run', 0) or exec_stats.get('not_executed', 0) or 0 if exec_stats else 0,
        'priority_distribution': priority_dist,
        'severity_distribution': severity_dist
    })


@dashboard_bp.route('/api/dashboard/trend')
@login_required
def get_trend():
    """API endpoint for execution trend data."""
    trend_data = Execution.get_trend(days=30)
    return jsonify(trend_data or [])


@dashboard_bp.route('/api/dashboard/module-stats')
@login_required
def get_module_stats():
    """API endpoint for module-wise pass percentage."""
    module_stats = Execution.get_module_wise_stats()
    return jsonify(module_stats or [])


@dashboard_bp.route('/api/dashboard/recent-activity')
@login_required
def get_recent_activity():
    """API endpoint for recent activities."""
    # Recent executions
    recent_executions = Execution.get_recent(limit=5) or []

    # Recent test cases
    recent_cases_query = """
        SELECT tc.test_id, tc.title, tc.priority, tc.created_date,
               u.full_name as creator_name
        FROM test_cases tc
        LEFT JOIN users u ON tc.created_by = u.id
        ORDER BY tc.created_date DESC
        LIMIT 5
    """
    recent_cases = execute_query(recent_cases_query, fetch_all=True) or []

    return jsonify({
        'recent_executions': recent_executions,
        'recent_cases': recent_cases
    })
