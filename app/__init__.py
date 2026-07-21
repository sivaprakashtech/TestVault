"""
Flask Application Factory
Initializes the Flask app with configuration, database, and route registration.
"""

import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'app/static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(
        os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    )

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize SQLite database (creates tables if they don't exist)
    from app.utils.database import init_db
    init_db()

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.projects import projects_bp
    from app.routes.test_suites import test_suites_bp
    from app.routes.test_cases import test_cases_bp
    from app.routes.executions import executions_bp
    from app.routes.bug_links import bug_links_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(test_suites_bp, url_prefix='/suites')
    app.register_blueprint(test_cases_bp, url_prefix='/test-cases')
    app.register_blueprint(executions_bp, url_prefix='/executions')
    app.register_blueprint(bug_links_bp, url_prefix='/bugs')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    return app
