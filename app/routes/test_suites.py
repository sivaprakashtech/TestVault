"""
Test Suite Routes
Handles full CRUD operations for test suites with search, pagination, and sorting.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.helpers import login_required
from app.models.test_suite import TestSuite
from app.models.project import Project

test_suites_bp = Blueprint('test_suites', __name__)


@test_suites_bp.route('/project/<int:project_id>')
@login_required
def by_project(project_id):
    """List all test suites for a project."""
    project = Project.get_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects.index'))

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    sort_by = request.args.get('sort', 'created_date')
    sort_order = request.args.get('order', 'DESC')

    filters = {}
    if search:
        filters['search'] = search
    if status:
        filters['status'] = status
    if priority:
        filters['priority'] = priority

    result = TestSuite.get_by_project(
        project_id,
        filters=filters,
        page=page,
        per_page=12,
        sort_by=sort_by,
        sort_order=sort_order
    )

    counts = TestSuite.get_count_by_project(project_id)

    return render_template(
        'test_suites/list.html',
        project=project,
        suites=result['items'],
        pagination=result,
        filters={'search': search, 'status': status, 'priority': priority,
                 'sort': sort_by, 'order': sort_order},
        counts=counts
    )


@test_suites_bp.route('/create/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create(project_id):
    """Create a new test suite."""
    project = Project.get_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'Medium')

        if not name:
            flash('Suite name is required.', 'error')
            return render_template('test_suites/create.html', project=project,
                                   data={'name': name, 'description': description, 'priority': priority})

        if priority not in ('Critical', 'High', 'Medium', 'Low'):
            flash('Invalid priority value.', 'error')
            return render_template('test_suites/create.html', project=project,
                                   data={'name': name, 'description': description, 'priority': priority})

        suite_id = TestSuite.create(project_id, name, description, priority, session['user_id'])
        flash(f'Test suite "{name}" created successfully!', 'success')
        return redirect(url_for('test_suites.view', suite_id=suite_id))

    return render_template('test_suites/create.html', project=project, data={})


@test_suites_bp.route('/<int:suite_id>')
@login_required
def view(suite_id):
    """View a test suite with stats."""
    suite = TestSuite.get_by_id(suite_id)
    if not suite:
        flash('Test suite not found.', 'error')
        return redirect(url_for('projects.index'))
    return render_template('test_suites/view.html', suite=suite)


@test_suites_bp.route('/<int:suite_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(suite_id):
    """Edit a test suite."""
    suite = TestSuite.get_by_id(suite_id)
    if not suite:
        flash('Test suite not found.', 'error')
        return redirect(url_for('projects.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'Medium')

        if not name:
            flash('Suite name is required.', 'error')
            suite['name'] = name
            suite['description'] = description
            suite['priority'] = priority
            return render_template('test_suites/edit.html', suite=suite)

        if priority not in ('Critical', 'High', 'Medium', 'Low'):
            flash('Invalid priority value.', 'error')
            return render_template('test_suites/edit.html', suite=suite)

        TestSuite.update(suite_id, name, description, priority)
        flash('Test suite updated successfully!', 'success')
        return redirect(url_for('test_suites.view', suite_id=suite_id))

    return render_template('test_suites/edit.html', suite=suite)


@test_suites_bp.route('/<int:suite_id>/archive', methods=['POST'])
@login_required
def archive(suite_id):
    """Archive or reactivate a test suite."""
    suite = TestSuite.get_by_id(suite_id)
    if not suite:
        flash('Test suite not found.', 'error')
        return redirect(url_for('projects.index'))

    if suite['status'] == 'Active':
        TestSuite.archive(suite_id)
        flash(f'Suite "{suite["name"]}" archived.', 'success')
    else:
        TestSuite.activate(suite_id)
        flash(f'Suite "{suite["name"]}" reactivated.', 'success')

    return redirect(url_for('test_suites.by_project', project_id=suite['project_id']))


@test_suites_bp.route('/<int:suite_id>/delete', methods=['POST'])
@login_required
def delete(suite_id):
    """Delete a test suite with all its test cases."""
    suite = TestSuite.get_by_id(suite_id)
    if not suite:
        flash('Test suite not found.', 'error')
        return redirect(url_for('projects.index'))

    project_id = suite['project_id']
    TestSuite.delete(suite_id)
    flash(f'Suite "{suite["name"]}" deleted permanently.', 'success')
    return redirect(url_for('test_suites.by_project', project_id=project_id))
