"""
Database Utility
Handles SQLite connection and query execution.
Uses Python's built-in sqlite3 module - no external DB install required.

Architecture Note:
    All queries use %s placeholders (MySQL-style) which are converted to ?
    (SQLite-style) at execution time. This makes migrating back to MySQL
    trivial - just swap this file and remove the placeholder conversion.

Testing Note:
    Set environment variable TESTING=1 to use test_database.db instead of
    the production qa_test_management.db. The production DB is NEVER touched
    during automated tests.
"""

import os
import sqlite3
from contextlib import contextmanager

# Database file path - stored in project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use test_database.db when TESTING env var is set, otherwise production DB
if os.environ.get('TESTING') == '1':
    DB_PATH = os.path.join(BASE_DIR, 'database', 'test_database.db')
else:
    DB_PATH = os.path.join(BASE_DIR, 'database', 'qa_test_management.db')


def _convert_placeholders(query):
    """Convert MySQL-style %s placeholders to SQLite-style ? placeholders."""
    return query.replace('%s', '?')


def dict_factory(cursor, row):
    """Convert SQLite rows to dictionaries (mimics MySQL dictionary cursor)."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


@contextmanager
def get_db_connection():
    """Get a database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = dict_factory
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        yield connection
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()


@contextmanager
def get_db_cursor(dictionary=True):
    """Get a database cursor with automatic connection management."""
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute a query and optionally fetch results."""
    query = _convert_placeholders(query)
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        if fetch_one:
            return cursor.fetchone()
        if fetch_all:
            return cursor.fetchall()
        return cursor.lastrowid


def execute_many(query, data):
    """Execute a query with multiple data sets."""
    query = _convert_placeholders(query)
    with get_db_cursor() as cursor:
        cursor.executemany(query, data)
        return cursor.rowcount


def init_db():
    """Initialize the database schema. Called on app startup."""
    schema_path = os.path.join(BASE_DIR, 'database', 'schema.sql')
    if not os.path.exists(schema_path):
        return

    with get_db_connection() as connection:
        with open(schema_path, 'r') as f:
            connection.executescript(f.read())

        # Migration: add project_key column if missing (for existing DBs)
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col['name'] for col in cursor.fetchall()]
        if 'project_key' not in columns:
            cursor.execute("ALTER TABLE projects ADD COLUMN project_key TEXT DEFAULT '' NOT NULL")
            cursor.execute("SELECT id, name FROM projects WHERE project_key = ''")
            for row in cursor.fetchall():
                key = row['name'][:4].upper().replace(' ', '')
                key = ''.join(c for c in key if c.isalnum())[:6] or 'PROJ'
                cursor.execute("SELECT id FROM projects WHERE project_key = ?", (key,))
                if cursor.fetchone():
                    key = f"{key}{row['id']}"
                cursor.execute("UPDATE projects SET project_key = ? WHERE id = ?", (key, row['id']))
            connection.commit()

        # Migration: add priority column to test_suites if missing
        cursor.execute("PRAGMA table_info(test_suites)")
        columns = [col['name'] for col in cursor.fetchall()]
        if 'priority' not in columns:
            cursor.execute("ALTER TABLE test_suites ADD COLUMN priority TEXT DEFAULT 'Medium'")
            connection.commit()

        # Migration: add type column to test_cases if missing
        cursor.execute("PRAGMA table_info(test_cases)")
        columns = [col['name'] for col in cursor.fetchall()]
        if 'type' not in columns:
            cursor.execute("ALTER TABLE test_cases ADD COLUMN type TEXT DEFAULT 'Functional'")
            connection.commit()

        # Migration: add actual_result and duration to executions if missing
        cursor.execute("PRAGMA table_info(executions)")
        columns = [col['name'] for col in cursor.fetchall()]
        if 'actual_result' not in columns:
            cursor.execute("ALTER TABLE executions ADD COLUMN actual_result TEXT DEFAULT ''")
            connection.commit()
        if 'duration' not in columns:
            cursor.execute("ALTER TABLE executions ADD COLUMN duration INTEGER")
            connection.commit()
        if 'comments' not in columns:
            cursor.execute("ALTER TABLE executions ADD COLUMN comments TEXT DEFAULT ''")
            # Migrate old 'notes' data to 'comments' if notes column exists
            if 'notes' in columns:
                cursor.execute("UPDATE executions SET comments = notes WHERE comments = '' OR comments IS NULL")
            connection.commit()
