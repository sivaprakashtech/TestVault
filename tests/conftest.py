"""
Test Configuration
Sets up an isolated test environment using test_database.db.
NEVER touches the production qa_test_management.db.
"""

import os
import sys

# CRITICAL: Set TESTING=1 BEFORE any app imports so database.py uses test_database.db
os.environ['TESTING'] = '1'

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

TEST_DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'test_database.db')
PROD_DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'qa_test_management.db')


def setup_test_app():
    """Create a fresh test app with a clean test database."""
    # Remove old test DB if exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    from app import create_app
    app = create_app()
    return app


def teardown_test_db():
    """Remove the test database after tests complete."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def verify_production_db_untouched():
    """Verify that production DB was never modified by tests."""
    from app.utils.database import DB_PATH
    assert DB_PATH == TEST_DB_PATH, (
        f"CRITICAL: DB_PATH points to {DB_PATH}, not the test database! "
        f"Tests would have modified production data."
    )
