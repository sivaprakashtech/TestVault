"""
Project Routes
Handles full CRUD operations for projects with search, pagination, and sorting.
"""

import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.helpers import login_required
from app.models.project import Project

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/')
@login_required
def index():
    """List all projects with filters, search, pagination, and sorting."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    sort_by = request.args.get('sort', 'created_date')
    sort_order = request.args.get('order', 'DESC')

    filters = {}
    if search:
        filters['search'] = search
    if status:
        filters['status'] = status

    result = Project.get_all(
        filters=filters,
        page=page,
        per_page=12,
        sort_by=sort_by,
        sort_order=sort_order
    )

    counts = Project.get_count_by_status()

    return render_template(
        'projects/list.html',
        projects=result['items'],
        pagination=result,
        filters={'search': search, 'status': status, 'sort': sort_by, 'order': sort_order},
        counts=counts
    )


@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new project."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        project_key = request.form.get('project_key', '').strip().upper()
        description = request.form.get('description', '').strip()

        # Validation
        errors = []
        if not name:
            errors.append('Project name is required.')
        if not project_key:
            errors.append('Project key is required.')
        elif not re.match(r'^[A-Z][A-Z0-9_]{1,9}$', project_key):
            errors.append('Project key must be 2-10 uppercase letters/numbers, starting with a letter.')
        elif Project.key_exists(project_key):
            errors.append(f'Project key "{project_key}" is already in use.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('projects/create.html', data={
                'name': name, 'project_key': project_key, 'description': description
            })

        project_id = Project.create(name, project_key, description, session['user_id'])
        flash(f'Project "{name}" created successfully!', 'success')
        return redirect(url_for('projects.view', project_id=project_id))

    return render_template('projects/create.html', data={})


@projects_bp.route('/<int:project_id>')
@login_required
def view(project_id):
    """View project details with stats."""
    project = Project.get_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects.index'))
    return render_template('projects/view.html', project=project)


@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    """Edit a project."""
    project = Project.get_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        project_key = request.form.get('project_key', '').strip().upper()
        description = request.form.get('description', '').strip()

        # Validation
        errors = []
        if not name:
            errors.append('Project name is required.')
        if not project_key:
            errors.append('Project key is required.')
        elif not re.match(r'^[A-Z][A-Z0-9_]{1,9}$', project_key):
            errors.append('Project key must be 2-10 uppercase letters/numbers, starting with a letter.')
        elif Project.key_exists(project_key, exclude_id=project_id):
            errors.append(f'Project key "{project_key}" is already in use.')

        if errors:
            for error in errors:
                flash(error, 'error')
            project['name'] = name
            project['project_key'] = project_key
            project['description'] = description
            return render_template('projects/edit.html', project=project)

        Project.update(project_id, name, project_key, description)
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects.view', project_id=project_id))

    return render_template('projects/edit.html', project=project)


@projects_bp.route('/<int:project_id>/archive', methods=['POST'])
@login_required
def archive(project_id):
    """Archive a project."""
    project = Project.get_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects.index'))

    if project['status'] == 'Active':
        Project.archive(project_id)
        flash(f'Project "{project["name"]}" archived.', 'success')
    else:
        Project.activate(project_id)
        flash(f'Project "{project["name"]}" reactivated.', 'success')

    return redirect(url_for('projects.index'))


@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete(project_id):
    """Delete a project with all its data."""
    project = Project.get_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects.index'))

    Project.delete(project_id)
    flash(f'Project "{project["name"]}" deleted permanently.', 'success')
    return redirect(url_for('projects.index'))
