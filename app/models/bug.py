"""
Bug Model
Handles bug management with full CRUD, linking, stats, and filtering.
"""

from app.utils.database import execute_query


class Bug:
    """Bug model for defect tracking."""

    SEVERITIES = ['Critical', 'High', 'Medium', 'Low']
    PRIORITIES = ['P1', 'P2', 'P3', 'P4']
    STATUSES = ['Open', 'In Progress', 'Fixed', 'Retest', 'Closed', 'Rejected']

    @staticmethod
    def create(data):
        """Create a new bug."""
        query = """
            INSERT INTO bugs
            (bug_id, title, description, steps_to_reproduce, expected_result,
             actual_result, severity, priority, status, module, environment,
             build_version, assigned_to, reported_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['bug_id'], data['title'], data.get('description', ''),
            data.get('steps_to_reproduce', ''), data.get('expected_result', ''),
            data.get('actual_result', ''), data.get('severity', 'Medium'),
            data.get('priority', 'P2'), data.get('status', 'Open'),
            data.get('module', ''), data.get('environment', ''),
            data.get('build_version', ''), data.get('assigned_to'),
            data['reported_by']
        )
        return execute_query(query, params)

    @staticmethod
    def get_next_bug_id():
        """Generate the next bug ID (BUG-0001, BUG-0002, ...)."""
        query = "SELECT bug_id FROM bugs ORDER BY id DESC LIMIT 1"
        result = execute_query(query, fetch_one=True)
        if result:
            last_num = int(result['bug_id'].split('-')[1])
            return f"BUG-{str(last_num + 1).zfill(4)}"
        return "BUG-0001"

    @staticmethod
    def get_all(filters=None, page=1, per_page=15):
        """Get all bugs with filters and pagination."""
        base_query = """
            SELECT b.*, u1.full_name as reporter_name, u2.full_name as assignee_name
            FROM bugs b
            LEFT JOIN users u1 ON b.reported_by = u1.id
            LEFT JOIN users u2 ON b.assigned_to = u2.id
            WHERE 1=1
        """
        params = []

        if filters:
            if filters.get('severity'):
                base_query += " AND b.severity = %s"
                params.append(filters['severity'])
            if filters.get('priority'):
                base_query += " AND b.priority = %s"
                params.append(filters['priority'])
            if filters.get('status'):
                base_query += " AND b.status = %s"
                params.append(filters['status'])
            if filters.get('module'):
                base_query += " AND b.module = %s"
                params.append(filters['module'])
            if filters.get('search'):
                base_query += " AND (b.title LIKE %s OR b.bug_id LIKE %s OR b.description LIKE %s)"
                st = f"%{filters['search']}%"
                params.extend([st, st, st])

        count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
        total_result = execute_query(count_query, params, fetch_one=True)
        total = total_result['total'] if total_result else 0

        sort_by = filters.get('sort', 'created_date') if filters else 'created_date'
        sort_order = filters.get('order', 'DESC') if filters else 'DESC'
        allowed = ['created_date', 'title', 'severity', 'priority', 'status', 'bug_id']
        if sort_by not in allowed:
            sort_by = 'created_date'

        base_query += f" ORDER BY b.{sort_by} {sort_order}"
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
    def get_by_id(bug_db_id):
        """Get a bug by database ID."""
        query = """
            SELECT b.*, u1.full_name as reporter_name, u2.full_name as assignee_name
            FROM bugs b
            LEFT JOIN users u1 ON b.reported_by = u1.id
            LEFT JOIN users u2 ON b.assigned_to = u2.id
            WHERE b.id = %s
        """
        return execute_query(query, (bug_db_id,), fetch_one=True)

    @staticmethod
    def update(bug_db_id, data):
        """Update a bug."""
        query = """
            UPDATE bugs SET
                title = %s, description = %s, steps_to_reproduce = %s,
                expected_result = %s, actual_result = %s, severity = %s,
                priority = %s, status = %s, module = %s, environment = %s,
                build_version = %s, assigned_to = %s, updated_date = datetime('now')
            WHERE id = %s
        """
        params = (
            data['title'], data.get('description', ''),
            data.get('steps_to_reproduce', ''), data.get('expected_result', ''),
            data.get('actual_result', ''), data.get('severity', 'Medium'),
            data.get('priority', 'P2'), data.get('status', 'Open'),
            data.get('module', ''), data.get('environment', ''),
            data.get('build_version', ''), data.get('assigned_to') or None,
            bug_db_id
        )
        execute_query(query, params)

    @staticmethod
    def delete(bug_db_id):
        """Delete a bug."""
        query = "DELETE FROM bugs WHERE id = %s"
        execute_query(query, (bug_db_id,))

    @staticmethod
    def get_stats():
        """Get overall bug statistics."""
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_bugs,
                SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) as closed,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'Fixed' THEN 1 ELSE 0 END) as fixed,
                SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical
            FROM bugs
        """
        return execute_query(query, fetch_one=True)

    @staticmethod
    def get_severity_distribution():
        """Get bug count by severity."""
        query = "SELECT severity, COUNT(*) as count FROM bugs GROUP BY severity ORDER BY count DESC"
        return execute_query(query, fetch_all=True)

    @staticmethod
    def get_status_distribution():
        """Get bug count by status."""
        query = "SELECT status, COUNT(*) as count FROM bugs GROUP BY status ORDER BY count DESC"
        return execute_query(query, fetch_all=True)

    # --- LINKING ---

    @staticmethod
    def link_to_case(bug_db_id, test_case_id, execution_id, linked_by):
        """Link a bug to a test case (optionally to a specific execution)."""
        query = """
            INSERT INTO bug_execution_links (bug_table_id, execution_id, test_case_id, linked_by)
            VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (bug_db_id, execution_id, test_case_id, linked_by))

    @staticmethod
    def unlink(link_id):
        """Remove a bug-case link."""
        query = "DELETE FROM bug_execution_links WHERE id = %s"
        execute_query(query, (link_id,))

    @staticmethod
    def get_links_for_case(test_case_id):
        """Get all bugs linked to a test case."""
        query = """
            SELECT bel.id as link_id, bel.linked_date, bel.execution_id,
                   b.id as bug_db_id, b.bug_id, b.title, b.severity, b.priority, b.status,
                   u.full_name as linker_name
            FROM bug_execution_links bel
            JOIN bugs b ON bel.bug_table_id = b.id
            LEFT JOIN users u ON bel.linked_by = u.id
            WHERE bel.test_case_id = %s
            ORDER BY bel.linked_date DESC
        """
        return execute_query(query, (test_case_id,), fetch_all=True)

    @staticmethod
    def get_links_for_bug(bug_db_id):
        """Get all test cases/executions linked to a bug."""
        query = """
            SELECT bel.id as link_id, bel.execution_id, bel.linked_date,
                   tc.id as case_id, tc.test_id, tc.title as case_title,
                   ts.name as suite_name, p.name as project_name,
                   e.result as exec_result, e.execution_date
            FROM bug_execution_links bel
            JOIN test_cases tc ON bel.test_case_id = tc.id
            LEFT JOIN test_suites ts ON tc.suite_id = ts.id
            LEFT JOIN projects p ON ts.project_id = p.id
            LEFT JOIN executions e ON bel.execution_id = e.id
            WHERE bel.bug_table_id = %s
            ORDER BY bel.linked_date DESC
        """
        return execute_query(query, (bug_db_id,), fetch_all=True)

    @staticmethod
    def get_modules():
        """Get distinct modules from bugs."""
        query = "SELECT DISTINCT module FROM bugs WHERE module != '' ORDER BY module"
        results = execute_query(query, fetch_all=True)
        return [r['module'] for r in results] if results else []
