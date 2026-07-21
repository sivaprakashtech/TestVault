"""
Bug Link Model
Handles bug linking data operations.
"""

from app.utils.database import execute_query


class BugLink:
    """Bug Link model for tracking bugs linked to test cases."""

    @staticmethod
    def create(data):
        """Create a new bug link."""
        query = """
            INSERT INTO bug_links
            (test_case_id, bug_id, bug_title, bug_status, bug_priority, linked_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data['test_case_id'], data['bug_id'], data['bug_title'],
            data['bug_status'], data['bug_priority'], data['linked_by']
        )
        return execute_query(query, params)

    @staticmethod
    def get_by_test_case(test_case_id):
        """Get all bug links for a test case."""
        query = """
            SELECT bl.*, u.full_name as linker_name
            FROM bug_links bl
            LEFT JOIN users u ON bl.linked_by = u.id
            WHERE bl.test_case_id = %s
            ORDER BY bl.linked_date DESC
        """
        return execute_query(query, (test_case_id,), fetch_all=True)

    @staticmethod
    def get_all(page=1, per_page=15):
        """Get all bug links with pagination."""
        count_query = "SELECT COUNT(*) as total FROM bug_links"
        total_result = execute_query(count_query, fetch_one=True)
        total = total_result['total'] if total_result else 0

        query = """
            SELECT bl.*, tc.test_id, tc.title as test_title,
                   u.full_name as linker_name
            FROM bug_links bl
            LEFT JOIN test_cases tc ON bl.test_case_id = tc.id
            LEFT JOIN users u ON bl.linked_by = u.id
            ORDER BY bl.linked_date DESC
            LIMIT %s OFFSET %s
        """
        offset = (page - 1) * per_page
        items = execute_query(query, (per_page, offset), fetch_all=True)

        return {
            'items': items or [],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
        }

    @staticmethod
    def update(link_id, data):
        """Update a bug link."""
        query = """
            UPDATE bug_links SET
                bug_id = %s, bug_title = %s,
                bug_status = %s, bug_priority = %s
            WHERE id = %s
        """
        params = (
            data['bug_id'], data['bug_title'],
            data['bug_status'], data['bug_priority'], link_id
        )
        execute_query(query, params)

    @staticmethod
    def delete(link_id):
        """Delete a bug link."""
        query = "DELETE FROM bug_links WHERE id = %s"
        execute_query(query, (link_id,))
