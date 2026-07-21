"""
Bug Management Routes
Handles full bug CRUD, linking to test cases/executions, dashboard stats.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.utils.helpers import login_required
from app.models.bug import Bug
from app.models.test_case import TestCase
from app.models.execution import Execution
from app.models.user import User

bug_links_bp = Blueprint('bug_links', __name__)


@bug_links_bp.route('/')
@login_required
def index():
    """List all bugs with filters and pagination."""
    page = request.args.get('page', 1, type=int)
    filters = {
        'severity': request.args.get('severity', ''),
        'priority': request.args.get('priority', ''),
        'status': request.args.get('status', ''),
        'search': request.args.get('search', '').strip(),
        'sort': request.args.get('sort', 'created_date'),
        'order': request.args.get('order', 'DESC'),
    }
    active_filters = {k: v for k, v in filters.items() if v}

    result = Bug.get_all(filters=active_filters, page=page)
    stats = Bug.get_stats()

    return render_template(
        'bugs/list.html',
        bugs=result['items'],
        pagination=result,
        filters=filters,
        stats=stats
    )


@bug_links_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new bug."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        severity = request.form.get('severity', 'Medium')
        priority = request.form.get('priority', 'P2')

        if not title:
            flash('Bug title is required.', 'error')
            return render_template('bugs/create.html', data=request.form)

        data = {
            'bug_id': Bug.get_next_bug_id(),
            'title': title,
            'description': request.form.get('description', '').strip(),
            'steps_to_reproduce': request.form.get('steps_to_reproduce', '').strip(),
            'expected_result': request.form.get('expected_result', '').strip(),
            'actual_result': request.form.get('actual_result', '').strip(),
            'severity': severity,
            'priority': priority,
            'status': request.form.get('status', 'Open'),
            'module': request.form.get('module', '').strip(),
            'environment': request.form.get('environment', '').strip(),
            'build_version': request.form.get('build_version', '').strip(),
            'assigned_to': request.form.get('assigned_to') or None,
            'reported_by': session['user_id']
        }

        bug_db_id = Bug.create(data)

        # If linking to a test case
        link_case_id = request.form.get('link_case_id')
        link_exec_id = request.form.get('link_execution_id')
        if link_case_id:
            Bug.link_to_case(bug_db_id, int(link_case_id), int(link_exec_id) if link_exec_id else None, session['user_id'])

        flash(f'Bug {data["bug_id"]} created!', 'success')
        return redirect(url_for('bug_links.view', bug_db_id=bug_db_id))

    # Pre-fill from test case if coming from there
    link_case_id = request.args.get('case_id')
    link_exec_id = request.args.get('exec_id')
    prefill = {}
    if link_case_id:
        tc = TestCase.get_by_id(int(link_case_id))
        if tc:
            prefill['link_case_id'] = link_case_id
            prefill['link_execution_id'] = link_exec_id or ''
            prefill['module'] = tc.get('module', '')
    return render_template('bugs/create.html', data=prefill)


@bug_links_bp.route('/<int:bug_db_id>')
@login_required
def view(bug_db_id):
    """View a bug with linked cases."""
    bug = Bug.get_by_id(bug_db_id)
    if not bug:
        flash('Bug not found.', 'error')
        return redirect(url_for('bug_links.index'))

    links = Bug.get_links_for_bug(bug_db_id)
    return render_template('bugs/view.html', bug=bug, links=links)


@bug_links_bp.route('/<int:bug_db_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(bug_db_id):
    """Edit a bug."""
    bug = Bug.get_by_id(bug_db_id)
    if not bug:
        flash('Bug not found.', 'error')
        return redirect(url_for('bug_links.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required.', 'error')
            return render_template('bugs/edit.html', bug=bug)

        data = {
            'title': title,
            'description': request.form.get('description', '').strip(),
            'steps_to_reproduce': request.form.get('steps_to_reproduce', '').strip(),
            'expected_result': request.form.get('expected_result', '').strip(),
            'actual_result': request.form.get('actual_result', '').strip(),
            'severity': request.form.get('severity', 'Medium'),
            'priority': request.form.get('priority', 'P2'),
            'status': request.form.get('status', 'Open'),
            'module': request.form.get('module', '').strip(),
            'environment': request.form.get('environment', '').strip(),
            'build_version': request.form.get('build_version', '').strip(),
            'assigned_to': request.form.get('assigned_to') or None,
        }

        Bug.update(bug_db_id, data)
        flash('Bug updated!', 'success')
        return redirect(url_for('bug_links.view', bug_db_id=bug_db_id))

    return render_template('bugs/edit.html', bug=bug)


@bug_links_bp.route('/<int:bug_db_id>/delete', methods=['POST'])
@login_required
def delete(bug_db_id):
    """Delete a bug."""
    bug = Bug.get_by_id(bug_db_id)
    if not bug:
        flash('Bug not found.', 'error')
        return redirect(url_for('bug_links.index'))

    Bug.delete(bug_db_id)
    flash(f'Bug {bug["bug_id"]} deleted.', 'success')
    return redirect(url_for('bug_links.index'))


@bug_links_bp.route('/link/<int:case_id>', methods=['GET', 'POST'])
@login_required
def link(case_id):
    """Link an existing bug to a test case."""
    test_case = TestCase.get_by_id(case_id)
    if not test_case:
        flash('Test case not found.', 'error')
        return redirect(url_for('test_cases.index'))

    if request.method == 'POST':
        bug_db_id = request.form.get('bug_db_id')
        exec_id = request.form.get('execution_id') or None

        if not bug_db_id:
            flash('Please select a bug to link.', 'error')
            bugs = Bug.get_all(per_page=100)
            return render_template('bugs/link.html', test_case=test_case, bugs=bugs['items'])

        Bug.link_to_case(int(bug_db_id), case_id, int(exec_id) if exec_id else None, session['user_id'])
        flash('Bug linked to test case!', 'success')
        return redirect(url_for('test_cases.view', case_id=case_id))

    bugs = Bug.get_all(per_page=100)
    return render_template('bugs/link.html', test_case=test_case, bugs=bugs['items'])


@bug_links_bp.route('/unlink/<int:link_id>', methods=['POST'])
@login_required
def unlink(link_id):
    """Remove a bug-case link."""
    Bug.unlink(link_id)
    flash('Bug unlinked.', 'success')
    return redirect(request.referrer or url_for('bug_links.index'))


@bug_links_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for bug statistics."""
    stats = Bug.get_stats()
    severity_dist = Bug.get_severity_distribution()
    status_dist = Bug.get_status_distribution()
    return jsonify({
        'stats': stats,
        'severity_distribution': severity_dist or [],
        'status_distribution': status_dist or []
    })
