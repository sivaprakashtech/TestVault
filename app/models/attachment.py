"""
Attachment Model
Handles file attachment data operations.
"""

from app.utils.database import execute_query


class Attachment:
    """Attachment model for screenshots, logs, and documents."""

    @staticmethod
    def create(data):
        """Create a new attachment record."""
        query = """
            INSERT INTO attachments
            (test_case_id, filename, original_name, file_type, file_size, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data['test_case_id'], data['filename'], data['original_name'],
            data['file_type'], data['file_size'], data['uploaded_by']
        )
        return execute_query(query, params)

    @staticmethod
    def get_by_test_case(test_case_id):
        """Get all attachments for a test case."""
        query = """
            SELECT a.*, u.full_name as uploader_name
            FROM attachments a
            LEFT JOIN users u ON a.uploaded_by = u.id
            WHERE a.test_case_id = %s
            ORDER BY a.uploaded_date DESC
        """
        return execute_query(query, (test_case_id,), fetch_all=True)

    @staticmethod
    def get_by_id(attachment_id):
        """Get an attachment by ID."""
        query = "SELECT * FROM attachments WHERE id = %s"
        return execute_query(query, (attachment_id,), fetch_one=True)

    @staticmethod
    def delete(attachment_id):
        """Delete an attachment record."""
        query = "DELETE FROM attachments WHERE id = %s"
        execute_query(query, (attachment_id,))
