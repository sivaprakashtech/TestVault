"""
Project Model
Handles project data operations with search, pagination, and stats.
"""

from app.utils.database import execute_query


class Project:
    """Project model - top level of the hierarchy."""

    @staticmethod
    def create(name, project_key, description, created_by):
        """Create a new project."""
        query = """
            INSERT INTO projects (name, project_key, description, created_by)
            VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (name, project_key, description, created_by))

    @staticmethod
    def get_all(filters=None, page=1, per_page=12, sort_by='created_date', sort_order='DESC'):
        """Get all projects with optional filters, pagination, and sorting."""
        base_query = """
            SELECT p.*, u.full_name as creator_name,
                   (SELECT COUNT(*) FROM test_suites WHERE project_id = p.id) as suite_count,
                   (SELECT COUNT(*) FROM test_cases tc
                    JOIN test_suites ts ON tc.suite_id = ts.id
                    WHERE ts.project_id = p.id) as case_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc2 ON e.test_case_id = tc2.id
                    JOIN test_suites ts2 ON tc2.suite_id = ts2.id
                    WHERE ts2.project_id = p.id) as exec_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc3 ON e.test_case_id = tc3.id
                    JOIN test_suites ts3 ON tc3.suite_id = ts3.id
                    WHERE ts3.project_id = p.id AND e.result = 'Passed') as passed_count
            FROM projects p
            LEFT JOIN users u ON p.created_by = u.id
            WHERE 1=1
        """
        params = []

        if filters:
            if filters.get('status'):
                base_query += " AND p.status = %s"
                params.append(filters['status'])
            if filters.get('search'):
                base_query += " AND (p.name LIKE %s OR p.project_key LIKE %s OR p.description LIKE %s)"
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term, search_term])

        # Count query
        count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
        total_result = execute_query(count_query, params, fetch_one=True)
        total = total_result['total'] if total_result else 0

        # Validate sort column to prevent injection
        allowed_sorts = ['created_date', 'name', 'project_key', 'updated_date']
        if sort_by not in allowed_sorts:
            sort_by = 'created_date'
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'

        base_query += f" ORDER BY p.{sort_by} {sort_order}"
        base_query += " LIMIT %s OFFSET %s"
        offset = (page - 1) * per_page
        params.extend([per_page, offset])

        items = execute_query(base_query, params, fetch_all=True)

        return {
            'items': items or [],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': max((total + per_page - 1) // per_page, 1)
        }

    @staticmethod
    def get_by_id(project_id):
        """Get a project by ID with full stats."""
        query = """
            SELECT p.*, u.full_name as creator_name,
                   (SELECT COUNT(*) FROM test_suites WHERE project_id = p.id) as suite_count,
                   (SELECT COUNT(*) FROM test_cases tc
                    JOIN test_suites ts ON tc.suite_id = ts.id
                    WHERE ts.project_id = p.id) as case_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc2 ON e.test_case_id = tc2.id
                    JOIN test_suites ts2 ON tc2.suite_id = ts2.id
                    WHERE ts2.project_id = p.id) as exec_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc3 ON e.test_case_id = tc3.id
                    JOIN test_suites ts3 ON tc3.suite_id = ts3.id
                    WHERE ts3.project_id = p.id AND e.result = 'Passed') as passed_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc4 ON e.test_case_id = tc4.id
                    JOIN test_suites ts4 ON tc4.suite_id = ts4.id
                    WHERE ts4.project_id = p.id AND e.result = 'Failed') as failed_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc5 ON e.test_case_id = tc5.id
                    JOIN test_suites ts5 ON tc5.suite_id = ts5.id
                    WHERE ts5.project_id = p.id AND e.result = 'Blocked') as blocked_count
            FROM projects p
            LEFT JOIN users u ON p.created_by = u.id
            WHERE p.id = %s
        """
        return execute_query(query, (project_id,), fetch_one=True)

    @staticmethod
    def update(project_id, name, project_key, description):
        """Update a project."""
        query = """
            UPDATE projects
            SET name = %s, project_key = %s, description = %s, updated_date = datetime('now')
            WHERE id = %s
        """
        execute_query(query, (name, project_key, description, project_id))

    @staticmethod
    def archive(project_id):
        """Archive a project."""
        query = "UPDATE projects SET status = 'Archived', updated_date = datetime('now') WHERE id = %s"
        execute_query(query, (project_id,))

    @staticmethod
    def activate(project_id):
        """Reactivate an archived project."""
        query = "UPDATE projects SET status = 'Active', updated_date = datetime('now') WHERE id = %s"
        execute_query(query, (project_id,))

    @staticmethod
    def delete(project_id):
        """Delete a project and cascade."""
        query = "DELETE FROM projects WHERE id = %s"
        execute_query(query, (project_id,))

    @staticmethod
    def key_exists(project_key, exclude_id=None):
        """Check if a project key already exists."""
        if exclude_id:
            query = "SELECT id FROM projects WHERE project_key = %s AND id != %s"
            result = execute_query(query, (project_key, exclude_id), fetch_one=True)
        else:
            query = "SELECT id FROM projects WHERE project_key = %s"
            result = execute_query(query, (project_key,), fetch_one=True)
        return result is not None

    @staticmethod
    def get_count_by_status():
        """Get project counts grouped by status."""
        query = """
            SELECT status, COUNT(*) as count
            FROM projects
            GROUP BY status
        """
        results = execute_query(query, fetch_all=True)
        counts = {'Active': 0, 'Archived': 0, 'total': 0}
        if results:
            for r in results:
                counts[r['status']] = r['count']
                counts['total'] += r['count']
        return counts
