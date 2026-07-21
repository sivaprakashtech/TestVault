"""
User Model
Handles user data operations for authentication.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.database import execute_query


class User:
    """User model for authentication and session management."""

    @staticmethod
    def create(full_name, email, password):
        """Create a new user with hashed password."""
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        query = """
            INSERT INTO users (full_name, email, password_hash)
            VALUES (%s, %s, %s)
        """
        return execute_query(query, (full_name, email, hashed_password))

    @staticmethod
    def find_by_email(email):
        """Find a user by email address."""
        query = "SELECT * FROM users WHERE email = %s"
        return execute_query(query, (email,), fetch_one=True)

    @staticmethod
    def find_by_id(user_id):
        """Find a user by ID."""
        query = "SELECT * FROM users WHERE id = %s"
        return execute_query(query, (user_id,), fetch_one=True)

    @staticmethod
    def verify_password(stored_hash, password):
        """Verify a password against its hash."""
        return check_password_hash(stored_hash, password)

    @staticmethod
    def update_last_login(user_id):
        """Update the last login timestamp."""
        query = "UPDATE users SET last_login = datetime('now') WHERE id = %s"
        execute_query(query, (user_id,))
