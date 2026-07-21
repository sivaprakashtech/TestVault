"""
Helper Utilities
Common helper functions used across the application.
"""

import os
import uuid
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from app.config import Config


def login_required(f):
    """Decorator to protect routes that require authentication.
    Also validates that the session user still exists in the database
    (handles cases where DB was reset but browser session persists).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        # Validate the user still exists in the database
        from app.models.user import User
        user = User.find_by_id(session['user_id'])
        if not user:
            session.clear()
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed."""
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


def save_file(file):
    """Save uploaded file and return the stored filename."""
    if file and allowed_file(file.filename):
        # Generate unique filename to prevent collisions
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_name)
        file.save(filepath)
        return unique_name
    return None


def format_datetime(dt):
    """Format datetime for display."""
    if not dt:
        return ''
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime('%b %d, %Y at %I:%M %p')


def format_date(dt):
    """Format date for display."""
    if not dt:
        return ''
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime('%b %d, %Y')


def generate_test_id(prefix='TC', last_id=0):
    """Generate next test case ID like TC-001, TC-002."""
    return f"{prefix}-{str(last_id + 1).zfill(4)}"


def paginate(items, page, per_page=Config.ITEMS_PER_PAGE):
    """Simple pagination helper for lists."""
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(items) + per_page - 1) // per_page
    return {
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': len(items),
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }
