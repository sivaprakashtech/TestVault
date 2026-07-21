"""
Test Case Routes
Handles full CRUD operations for test cases with search, filters, pagination.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.helpers import login_required
from app.models.test_case import TestCase
from app.models.test_suite import TestSuite
from app.models.project import Project

test_cases_bp = Blueprint('test_cases', __name__)


@test_cases_bp.route('/')
@login_required
def index():
    """List all test cases with filters and pagination."""
    page = request.args.get('page', 1, type=int)
    filters = {
        'suite_id': request.args.get('suite_id'),
        'project_id': request.args.get('project_id'),
        'priority': request.args.get('priority', ''),
        'type': request.args.get('type', ''),
        'status': request.args.get('status', ''),
        'severity': request.args.get('severity', ''),
        'search': request.args.get('search', '').strip(),
        'sort': request.args.get('sort', 'created_date'),
        'order': request.args.get('order', 'DESC'),
    }
    # Remove empty values
    active_filters = {k: v for k, v in filters.items() if v}

    result = TestCase.get_all(filters=active_filters, page=page)
    modules = TestCase.get_modules()

    return render_template(
        'test_cases/list.html',
        test_cases=result['items'],
        pagination=result,
        filters=filters,
        modules=modules
    )


@test_cases_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new test case."""
    if request.method == 'POST':
        suite_id = request.form.get('suite_id')
        title = request.form.get('title', '').strip()
        steps = request.form.get('steps', '').strip()
        expected_result = request.form.get('expected_result', '').strip()
        priority = request.form.get('priority', 'Medium')
        tc_type = request.form.get('type', 'Functional')

        # Validation
        errors = []
        if not title:
            errors.append('Title is required.')
        if not suite_id:
            errors.append('Test Suite is required.')
        if not steps:
            errors.append('Test Steps are required.')
        if not expected_result:
            errors.append('Expected Result is required.')
        if priority not in TestCase.PRIORITIES:
            errors.append('Invalid priority.')
        if tc_type not in TestCase.TYPES:
            errors.append('Invalid type.')

        if errors:
            for e in errors:
                flash(e, 'error')
            suites = TestSuite.get_all()
            return render_template('test_cases/create.html', suites=suites, data=request.form)

        data = {
            'test_id': TestCase.get_next_test_id(),
            'suite_id': suite_id,
            'title': title,
            'description': request.form.get('description', '').strip(),
            'preconditions': request.form.get('preconditions', '').strip(),
            'steps': steps,
            'expected_result': expected_result,
            'module': request.form.get('module', '').strip(),
            'feature': request.form.get('feature', '').strip(),
            'priority': priority,
            'severity': request.form.get('severity', 'Major'),
            'type': tc_type,
            'status': request.form.get('status', 'Draft'),
            'created_by': session['user_id']
        }

        case_id = TestCase.create(data)
        flash(f'Test case {data["test_id"]} created successfully!', 'success')
        return redirect(url_for('test_cases.view', case_id=case_id))

    suites = TestSuite.get_all()
    return render_template('test_cases/create.html', suites=suites, data={})


@test_cases_bp.route('/<int:case_id>')
@login_required
def view(case_id):
    """View a test case."""
    test_case = TestCase.get_by_id(case_id)
    if not test_case:
        flash('Test case not found.', 'error')
        return redirect(url_for('test_cases.index'))
    return render_template('test_cases/view.html', test_case=test_case)


@test_cases_bp.route('/<int:case_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(case_id):
    """Edit a test case."""
    test_case = TestCase.get_by_id(case_id)
    if not test_case:
        flash('Test case not found.', 'error')
        return redirect(url_for('test_cases.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        steps = request.form.get('steps', '').strip()
        expected_result = request.form.get('expected_result', '').strip()

        if not title or not steps or not expected_result:
            flash('Title, Steps, and Expected Result are required.', 'error')
            return render_template('test_cases/edit.html', test_case=test_case, suites=TestSuite.get_all())

        data = {
            'title': title,
            'description': request.form.get('description', '').strip(),
            'preconditions': request.form.get('preconditions', '').strip(),
            'steps': steps,
            'expected_result': expected_result,
            'module': request.form.get('module', '').strip(),
            'feature': request.form.get('feature', '').strip(),
            'priority': request.form.get('priority', 'Medium'),
            'severity': request.form.get('severity', 'Major'),
            'type': request.form.get('type', 'Functional'),
            'status': request.form.get('status', 'Draft')
        }

        TestCase.update(case_id, data)
        flash('Test case updated successfully!', 'success')
        return redirect(url_for('test_cases.view', case_id=case_id))

    suites = TestSuite.get_all()
    return render_template('test_cases/edit.html', test_case=test_case, suites=suites)


@test_cases_bp.route('/<int:case_id>/delete', methods=['POST'])
@login_required
def delete(case_id):
    """Delete a test case."""
    test_case = TestCase.get_by_id(case_id)
    if not test_case:
        flash('Test case not found.', 'error')
        return redirect(url_for('test_cases.index'))

    TestCase.delete(case_id)
    flash(f'Test case {test_case["test_id"]} deleted.', 'success')
    return redirect(url_for('test_cases.index'))


@test_cases_bp.route('/<int:case_id>/duplicate', methods=['POST'])
@login_required
def duplicate(case_id):
    """Duplicate a test case."""
    new_id = TestCase.duplicate(case_id, session['user_id'])
    if new_id:
        flash('Test case duplicated!', 'success')
        return redirect(url_for('test_cases.view', case_id=new_id))
    flash('Failed to duplicate.', 'error')
    return redirect(url_for('test_cases.view', case_id=case_id))


@test_cases_bp.route('/<int:case_id>/archive', methods=['POST'])
@login_required
def archive(case_id):
    """Archive or restore a test case."""
    test_case = TestCase.get_by_id(case_id)
    if not test_case:
        flash('Test case not found.', 'error')
        return redirect(url_for('test_cases.index'))

    if test_case['status'] == 'Deprecated':
        TestCase.restore(case_id)
        flash(f'{test_case["test_id"]} restored.', 'success')
    else:
        TestCase.archive(case_id)
        flash(f'{test_case["test_id"]} archived.', 'success')

    return redirect(url_for('test_cases.index'))
