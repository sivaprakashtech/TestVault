"""
Execution Routes
Handles test case execution with history, filters, pagination.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.helpers import login_required
from app.models.execution import Execution
from app.models.test_case import TestCase

executions_bp = Blueprint('executions', __name__)


@executions_bp.route('/')
@login_required
def index():
    """List all executions with filters and pagination."""
    page = request.args.get('page', 1, type=int)
    filters = {
        'result': request.args.get('result', ''),
        'environment': request.args.get('environment', ''),
        'date_from': request.args.get('date_from', ''),
        'date_to': request.args.get('date_to', ''),
        'search': request.args.get('search', '').strip(),
        'sort': request.args.get('sort', 'execution_date'),
        'order': request.args.get('order', 'DESC'),
    }
    active_filters = {k: v for k, v in filters.items() if v}

    result = Execution.get_all(filters=active_filters, page=page)
    stats = Execution.get_stats()

    return render_template(
        'executions/list.html',
        executions=result['items'],
        pagination=result,
        filters=filters,
        stats=stats
    )


@executions_bp.route('/execute/<int:case_id>', methods=['GET', 'POST'])
@login_required
def execute(case_id):
    """Execute a test case."""
    test_case = TestCase.get_by_id(case_id)
    if not test_case:
        flash('Test case not found.', 'error')
        return redirect(url_for('test_cases.index'))

    if request.method == 'POST':
        result_val = request.form.get('result', '')
        actual_result = request.form.get('actual_result', '').strip()
        environment = request.form.get('environment', 'QA')
        build_version = request.form.get('build_version', '').strip()
        duration = request.form.get('duration', '').strip()
        comments = request.form.get('comments', '').strip()

        # Validation
        if not result_val or result_val not in Execution.RESULTS:
            flash('Please select a valid execution result.', 'error')
            return render_template('executions/execute.html', test_case=test_case, data=request.form)

        data = {
            'test_case_id': case_id,
            'result': result_val,
            'actual_result': actual_result,
            'executed_by': session['user_id'],
            'environment': environment,
            'build_version': build_version,
            'duration': int(duration) if duration.isdigit() else None,
            'comments': comments
        }

        exec_id = Execution.create(data)
        flash(f'{test_case["test_id"]} executed as {result_val}!', 'success')
        return redirect(url_for('executions.view_result', exec_id=exec_id))

    return render_template('executions/execute.html', test_case=test_case, data={})


@executions_bp.route('/result/<int:exec_id>')
@login_required
def view_result(exec_id):
    """View a single execution result."""
    execution = Execution.get_by_id(exec_id)
    if not execution:
        flash('Execution not found.', 'error')
        return redirect(url_for('executions.index'))
    return render_template('executions/view.html', execution=execution)


@executions_bp.route('/history/<int:case_id>')
@login_required
def history(case_id):
    """View execution history for a test case."""
    test_case = TestCase.get_by_id(case_id)
    if not test_case:
        flash('Test case not found.', 'error')
        return redirect(url_for('test_cases.index'))

    executions = Execution.get_by_test_case(case_id)
    return render_template('executions/history.html', test_case=test_case, executions=executions)
