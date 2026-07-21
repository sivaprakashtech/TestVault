"""
Test Case Model
Handles test case data operations with search, pagination, filtering, and sorting.
"""

from app.utils.database import execute_query


class TestCase:
    """Test Case model - lowest level of the hierarchy (Project → Suite → Case)."""

    PRIORITIES = ['Critical', 'High', 'Medium', 'Low']
    TYPES = ['Functional', 'Regression', 'Smoke', 'Sanity', 'API', 'UI']
    STATUSES = ['Draft', 'Ready', 'Active', 'Deprecated']
    SEVERITIES = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']

    @staticmethod
    def create(data):
        """Create a new test case."""
        query = """
            INSERT INTO test_cases
            (test_id, suite_id, title, description, preconditions,
             steps, expected_result, module, feature, priority,
             severity, type, status, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['test_id'], data['suite_id'], data['title'],
            data.get('description', ''), data.get('preconditions', ''),
            data['steps'], data['expected_result'],
            data.get('module', ''), data.get('feature', ''),
            data['priority'], data.get('severity', 'Major'),
            data.get('type', 'Functional'), data.get('status', 'Draft'),
            data['created_by']
        )
        return execute_query(query, params)

    @staticmethod
    def get_all(filters=None, page=1, per_page=15):
        """Get all test cases with optional filters and pagination."""
        base_query = """
            SELECT tc.*, ts.name as suite_name, p.name as project_name,
                   p.project_key, u.full_name as creator_name,
                   (SELECT result FROM executions
                    WHERE test_case_id = tc.id
                    ORDER BY execution_date DESC LIMIT 1) as last_result
            FROM test_cases tc
            LEFT JOIN test_suites ts ON tc.suite_id = ts.id
            LEFT JOIN projects p ON ts.project_id = p.id
            LEFT JOIN users u ON tc.created_by = u.id
            WHERE 1=1
        """
        params = []

        if filters:
            if filters.get('suite_id'):
                base_query += " AND tc.suite_id = %s"
                params.append(filters['suite_id'])
            if filters.get('project_id'):
                base_query += " AND ts.project_id = %s"
                params.append(filters['project_id'])
            if filters.get('priority'):
                base_query += " AND tc.priority = %s"
                params.append(filters['priority'])
            if filters.get('type'):
                base_query += " AND tc.type = %s"
                params.append(filters['type'])
            if filters.get('severity'):
                base_query += " AND tc.severity = %s"
                params.append(filters['severity'])
            if filters.get('status'):
                base_query += " AND tc.status = %s"
                params.append(filters['status'])
            if filters.get('module'):
                base_query += " AND tc.module = %s"
                params.append(filters['module'])
            if filters.get('search'):
                base_query += " AND (tc.title LIKE %s OR tc.test_id LIKE %s OR tc.description LIKE %s)"
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term, search_term])

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
        total_result = execute_query(count_query, params, fetch_one=True)
        total = total_result['total'] if total_result else 0

        # Sorting
        sort_by = filters.get('sort', 'created_date') if filters else 'created_date'
        sort_order = filters.get('order', 'DESC') if filters else 'DESC'
        allowed_sorts = ['created_date', 'title', 'priority', 'type', 'status', 'test_id']
        if sort_by not in allowed_sorts:
            sort_by = 'created_date'
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'

        base_query += f" ORDER BY tc.{sort_by} {sort_order}"
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
    def get_by_id(case_id):
        """Get a test case by ID with full context."""
        query = """
            SELECT tc.*, ts.name as suite_name, p.name as project_name,
                   p.id as project_id, p.project_key, u.full_name as creator_name
            FROM test_cases tc
            LEFT JOIN test_suites ts ON tc.suite_id = ts.id
            LEFT JOIN projects p ON ts.project_id = p.id
            LEFT JOIN users u ON tc.created_by = u.id
            WHERE tc.id = %s
        """
        return execute_query(query, (case_id,), fetch_one=True)

    @staticmethod
    def update(case_id, data):
        """Update a test case."""
        query = """
            UPDATE test_cases SET
                title = %s, description = %s, preconditions = %s,
                steps = %s, expected_result = %s, module = %s,
                feature = %s, priority = %s, severity = %s,
                type = %s, status = %s, updated_date = datetime('now')
            WHERE id = %s
        """
        params = (
            data['title'], data.get('description', ''),
            data.get('preconditions', ''), data['steps'],
            data['expected_result'], data.get('module', ''),
            data.get('feature', ''), data['priority'],
            data.get('severity', 'Major'), data.get('type', 'Functional'),
            data.get('status', 'Draft'), case_id
        )
        execute_query(query, params)

    @staticmethod
    def delete(case_id):
        """Delete a test case."""
        query = "DELETE FROM test_cases WHERE id = %s"
        execute_query(query, (case_id,))

    @staticmethod
    def archive(case_id):
        """Archive (deprecate) a test case."""
        query = "UPDATE test_cases SET status = 'Deprecated', updated_date = datetime('now') WHERE id = %s"
        execute_query(query, (case_id,))

    @staticmethod
    def restore(case_id):
        """Restore a deprecated test case to Draft."""
        query = "UPDATE test_cases SET status = 'Draft', updated_date = datetime('now') WHERE id = %s"
        execute_query(query, (case_id,))

    @staticmethod
    def get_next_test_id():
        """Generate the next test case ID (TC-0001, TC-0002, ...)."""
        query = "SELECT test_id FROM test_cases ORDER BY id DESC LIMIT 1"
        result = execute_query(query, fetch_one=True)
        if result:
            last_num = int(result['test_id'].split('-')[1])
            return f"TC-{str(last_num + 1).zfill(4)}"
        return "TC-0001"

    @staticmethod
    def duplicate(case_id, created_by):
        """Duplicate a test case."""
        original = TestCase.get_by_id(case_id)
        if not original:
            return None
        new_test_id = TestCase.get_next_test_id()
        data = {
            'test_id': new_test_id,
            'suite_id': original['suite_id'],
            'title': f"{original['title']} (Copy)",
            'description': original['description'],
            'preconditions': original['preconditions'],
            'steps': original['steps'],
            'expected_result': original['expected_result'],
            'module': original['module'],
            'feature': original['feature'],
            'priority': original['priority'],
            'severity': original['severity'],
            'type': original['type'],
            'status': 'Draft',
            'created_by': created_by
        }
        return TestCase.create(data)

    @staticmethod
    def get_modules():
        """Get distinct modules."""
        query = "SELECT DISTINCT module FROM test_cases WHERE module != '' ORDER BY module"
        results = execute_query(query, fetch_all=True)
        return [r['module'] for r in results] if results else []

    @staticmethod
    def get_features():
        """Get distinct features."""
        query = "SELECT DISTINCT feature FROM test_cases WHERE feature != '' ORDER BY feature"
        results = execute_query(query, fetch_all=True)
        return [r['feature'] for r in results] if results else []
