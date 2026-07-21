"""
Test Suite Model
Handles test suite data operations with search, pagination, and sorting.
"""

from app.utils.database import execute_query


class TestSuite:
    """Test Suite model - middle level of the hierarchy (Project → Suite → Case)."""

    @staticmethod
    def create(project_id, name, description, priority, created_by):
        """Create a new test suite."""
        query = """
            INSERT INTO test_suites (project_id, name, description, priority, created_by)
            VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (project_id, name, description, priority, created_by))

    @staticmethod
    def get_by_project(project_id, filters=None, page=1, per_page=12,
                       sort_by='created_date', sort_order='DESC'):
        """Get all test suites for a project with filters, pagination, sorting."""
        base_query = """
            SELECT ts.*, u.full_name as creator_name,
                   (SELECT COUNT(*) FROM test_cases WHERE suite_id = ts.id) as case_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc ON e.test_case_id = tc.id
                    WHERE tc.suite_id = ts.id) as exec_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc ON e.test_case_id = tc.id
                    WHERE tc.suite_id = ts.id AND e.result = 'Passed') as passed_count
            FROM test_suites ts
            LEFT JOIN users u ON ts.created_by = u.id
            WHERE ts.project_id = %s
        """
        params = [project_id]

        if filters:
            if filters.get('status'):
                base_query += " AND ts.status = %s"
                params.append(filters['status'])
            if filters.get('priority'):
                base_query += " AND ts.priority = %s"
                params.append(filters['priority'])
            if filters.get('search'):
                base_query += " AND (ts.name LIKE %s OR ts.description LIKE %s)"
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term])

        # Count
        count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
        total_result = execute_query(count_query, params, fetch_one=True)
        total = total_result['total'] if total_result else 0

        # Sort validation
        allowed_sorts = ['created_date', 'name', 'priority', 'updated_date']
        if sort_by not in allowed_sorts:
            sort_by = 'created_date'
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'

        base_query += f" ORDER BY ts.{sort_by} {sort_order}"
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
    def get_all():
        """Get all test suites across all projects."""
        query = """
            SELECT ts.*, p.name as project_name, p.project_key,
                   u.full_name as creator_name,
                   (SELECT COUNT(*) FROM test_cases WHERE suite_id = ts.id) as case_count
            FROM test_suites ts
            LEFT JOIN projects p ON ts.project_id = p.id
            LEFT JOIN users u ON ts.created_by = u.id
            ORDER BY ts.created_date DESC
        """
        return execute_query(query, fetch_all=True)

    @staticmethod
    def get_by_id(suite_id):
        """Get a test suite by ID with full stats."""
        query = """
            SELECT ts.*, p.name as project_name, p.id as project_id, p.project_key,
                   u.full_name as creator_name,
                   (SELECT COUNT(*) FROM test_cases WHERE suite_id = ts.id) as case_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc ON e.test_case_id = tc.id
                    WHERE tc.suite_id = ts.id) as exec_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc ON e.test_case_id = tc.id
                    WHERE tc.suite_id = ts.id AND e.result = 'Passed') as passed_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc ON e.test_case_id = tc.id
                    WHERE tc.suite_id = ts.id AND e.result = 'Failed') as failed_count,
                   (SELECT COUNT(*) FROM executions e
                    JOIN test_cases tc ON e.test_case_id = tc.id
                    WHERE tc.suite_id = ts.id AND e.result = 'Blocked') as blocked_count
            FROM test_suites ts
            LEFT JOIN projects p ON ts.project_id = p.id
            LEFT JOIN users u ON ts.created_by = u.id
            WHERE ts.id = %s
        """
        return execute_query(query, (suite_id,), fetch_one=True)

    @staticmethod
    def update(suite_id, name, description, priority):
        """Update a test suite."""
        query = """
            UPDATE test_suites
            SET name = %s, description = %s, priority = %s, updated_date = datetime('now')
            WHERE id = %s
        """
        execute_query(query, (name, description, priority, suite_id))

    @staticmethod
    def archive(suite_id):
        """Archive a test suite."""
        query = "UPDATE test_suites SET status = 'Archived', updated_date = datetime('now') WHERE id = %s"
        execute_query(query, (suite_id,))

    @staticmethod
    def activate(suite_id):
        """Reactivate an archived test suite."""
        query = "UPDATE test_suites SET status = 'Active', updated_date = datetime('now') WHERE id = %s"
        execute_query(query, (suite_id,))

    @staticmethod
    def delete(suite_id):
        """Delete a test suite and cascade to test cases."""
        query = "DELETE FROM test_suites WHERE id = %s"
        execute_query(query, (suite_id,))

    @staticmethod
    def get_count_by_project(project_id):
        """Get suite counts grouped by status for a project."""
        query = """
            SELECT status, COUNT(*) as count
            FROM test_suites
            WHERE project_id = %s
            GROUP BY status
        """
        results = execute_query(query, (project_id,), fetch_all=True)
        counts = {'Active': 0, 'Archived': 0, 'total': 0}
        if results:
            for r in results:
                counts[r['status']] = r['count']
                counts['total'] += r['count']
        return counts
