"""
Reports & Analytics Routes
Full analytics dashboard with charts, trends, exports, and project health.
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.helpers import login_required
from app.utils.export import export_to_csv, export_to_excel
from app.services.report_service import ReportService

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/')
@login_required
def index():
    """Render the reports & analytics page."""
    summary = ReportService.get_summary()
    project_reports = ReportService.get_project_reports()
    tester_analytics = ReportService.get_tester_analytics()
    critical_bugs = ReportService.get_critical_bugs()
    newest_bugs = ReportService.get_newest_bugs()
    closed_bugs = ReportService.get_recently_closed_bugs()
    active_modules = ReportService.get_most_active_modules()

    return render_template('reports/index.html',
                           summary=summary,
                           project_reports=project_reports,
                           tester_analytics=tester_analytics,
                           critical_bugs=critical_bugs,
                           newest_bugs=newest_bugs,
                           closed_bugs=closed_bugs,
                           active_modules=active_modules)


# --- JSON APIs for Charts ---

@reports_bp.route('/api/summary')
@login_required
def api_summary():
    """API: Summary stats."""
    return jsonify(ReportService.get_summary())


@reports_bp.route('/api/execution-distribution')
@login_required
def api_exec_distribution():
    """API: Execution results distribution."""
    return jsonify(ReportService.get_execution_distribution())


@reports_bp.route('/api/bug-severity')
@login_required
def api_bug_severity():
    """API: Bug severity distribution."""
    return jsonify(ReportService.get_bug_severity_distribution())


@reports_bp.route('/api/bug-status')
@login_required
def api_bug_status():
    """API: Bug status distribution."""
    return jsonify(ReportService.get_bug_status_distribution())


@reports_bp.route('/api/case-priority')
@login_required
def api_case_priority():
    """API: Test case priority distribution."""
    return jsonify(ReportService.get_case_priority_distribution())


@reports_bp.route('/api/execution-trend')
@login_required
def api_exec_trend():
    """API: Execution trend (7/30/90 days)."""
    days = request.args.get('days', 30, type=int)
    if days not in (7, 30, 90):
        days = 30
    return jsonify(ReportService.get_execution_trend(days))


@reports_bp.route('/api/bug-trend')
@login_required
def api_bug_trend():
    """API: Bug creation trend."""
    days = request.args.get('days', 30, type=int)
    if days not in (7, 30, 90):
        days = 30
    return jsonify(ReportService.get_bug_trend(days))


@reports_bp.route('/api/pass-rate-trend')
@login_required
def api_pass_rate_trend():
    """API: Pass rate trend."""
    days = request.args.get('days', 30, type=int)
    if days not in (7, 30, 90):
        days = 30
    return jsonify(ReportService.get_pass_rate_trend(days))


@reports_bp.route('/api/project-reports')
@login_required
def api_project_reports():
    """API: Per-project reports."""
    return jsonify(ReportService.get_project_reports())


@reports_bp.route('/api/tester-analytics')
@login_required
def api_tester_analytics():
    """API: Tester performance."""
    return jsonify(ReportService.get_tester_analytics())


# --- Export ---

@reports_bp.route('/export/<report_type>/<format_type>')
@login_required
def export(report_type, format_type):
    """Export report as CSV or Excel."""
    if report_type not in ('executions', 'bugs', 'projects'):
        report_type = 'executions'

    headers, data = ReportService.get_export_data(report_type)
    filename = f'{report_type}_report'

    if format_type == 'csv':
        return export_to_csv(data, headers, f'{filename}.csv')
    elif format_type == 'excel':
        return export_to_excel(data, headers, f'{filename}.xlsx', report_type.title())

    return export_to_csv(data, headers, f'{filename}.csv')
