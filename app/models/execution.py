"""
Execution Model
Handles test execution data operations with history, stats, and filtering.
"""

from app.utils.database import execute_query


class Execution:
    """Execution model for tracking test case runs."""

    RESULTS = ['Passed', 'Failed', 'Blocked', 'Not Run']
    ENVIRONMENTS = ['QA', 'UAT', 'Production', 'Development', 'Staging']

    @staticmethod
    def create(data):
        """Create a new execution record."""
        query = """
            INSERT INTO executions
            (test_case_id, result, actual_result, executed_by,
             environment, build_version, duration, comments)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['test_case_id'], data['result'],
            data.get('actual_result', ''), data['executed_by'],
            data.get('environment', 'QA'), data.get('build_version', ''),
            data.get('duration'), data.get('comments', '')
        )
        return execute_query(query, params)

    @staticmethod
    def get_by_id(exec_id):
        """Get a single execution by ID."""
        query = """
            SELECT e.*, tc.test_id, tc.title as test_title, tc.suite_id,
                   ts.name as suite_name, p.name as project_name,
                   u.full_name as executor_name
            FROM executions e
            LEFT JOIN test_cases tc ON e.test_case_id = tc.id
            LEFT JOIN test_suites ts ON tc.suite_id = ts.id
            LEFT JOIN projects p ON ts.project_id = p.id
            LEFT JOIN users u ON e.executed_by = u.id
            WHERE e.id = %s
        """
        return execute_query(query, (exec_id,), fetch_one=True)

    @staticmethod
    def get_by_test_case(test_case_id):
        """Get full execution history for a test case."""
        query = """
            SELECT e.*, u.full_name as executor_name
            FROM executions e
            LEFT JOIN users u ON e.executed_by = u.id
            WHERE e.test_case_id = %s
            ORDER BY e.execution_date DESC
        """
        return execute_query(query, (test_case_id,), fetch_all=True)

    @staticmethod
    def get_latest_for_case(test_case_id):
        """Get the most recent execution for a test case."""
        query = """
            SELECT e.*, u.full_name as executor_name
            FROM executions e
            LEFT JOIN users u ON e.executed_by = u.id
            WHERE e.test_case_id = %s
            ORDER BY e.execution_date DESC LIMIT 1
        """
        return execute_query(query, (test_case_id,), fetch_one=True)

    @staticmethod
    def get_all(filters=None, page=1, per_page=15):
        """Get all executions with filters and pagination."""
        base_query = """
            SELECT e.*, tc.test_id, tc.title as test_title,
                   ts.name as suite_name, p.name as project_name,
                   u.full_name as executor_name
            FROM executions e
            LEFT JOIN test_cases tc ON e.test_case_id = tc.id
            LEFT JOIN test_suites ts ON tc.suite_id = ts.id
            LEFT JOIN projects p ON ts.project_id = p.id
            LEFT JOIN users u ON e.executed_by = u.id
            WHERE 1=1
        """
        params = []

        if filters:
            if filters.get('result'):
                base_query += " AND e.result = %s"
                params.append(filters['result'])
            if filters.get('environment'):
                base_query += " AND e.environment = %s"
                params.append(filters['environment'])
            if filters.get('executed_by'):
                base_query += " AND e.executed_by = %s"
                params.append(filters['executed_by'])
            if filters.get('test_case_id'):
                base_query += " AND e.test_case_id = %s"
                params.append(filters['test_case_id'])
            if filters.get('suite_id'):
                base_query += " AND tc.suite_id = %s"
                params.append(filters['suite_id'])
            if filters.get('date_from'):
                base_query += " AND e.execution_date >= %s"
                params.append(filters['date_from'])
            if filters.get('date_to'):
                base_query += " AND e.execution_date <= %s"
                params.append(filters['date_to'] + ' 23:59:59')
            if filters.get('search'):
                base_query += " AND (tc.test_id LIKE %s OR tc.title LIKE %s)"
                st = f"%{filters['search']}%"
                params.extend([st, st])

        # Count
        count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
        total_result = execute_query(count_query, params, fetch_one=True)
        total = total_result['total'] if total_result else 0

        # Sort
        sort_by = filters.get('sort', 'execution_date') if filters else 'execution_date'
        sort_order = filters.get('order', 'DESC') if filters else 'DESC'
        allowed = ['execution_date', 'result', 'environment']
        if sort_by not in allowed:
            sort_by = 'execution_date'
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'

        base_query += f" ORDER BY e.{sort_by} {sort_order}"
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
    def get_recent(limit=10):
        """Get most recent executions."""
        query = """
            SELECT e.*, tc.test_id, tc.title as test_title,
                   u.full_name as executor_name
            FROM executions e
            LEFT JOIN test_cases tc ON e.test_case_id = tc.id
            LEFT JOIN users u ON e.executed_by = u.id
            ORDER BY e.execution_date DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch_all=True)

    @staticmethod
    def get_stats():
        """Get overall execution statistics."""
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN result = 'Passed' THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN result = 'Failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN result = 'Blocked' THEN 1 ELSE 0 END) as blocked,
                SUM(CASE WHEN result = 'Not Run' THEN 1 ELSE 0 END) as not_run
            FROM executions
        """
        return execute_query(query, fetch_one=True)

    @staticmethod
    def get_stats_for_suite(suite_id):
        """Get execution stats for a test suite."""
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN e.result = 'Passed' THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN e.result = 'Failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN e.result = 'Blocked' THEN 1 ELSE 0 END) as blocked,
                SUM(CASE WHEN e.result = 'Not Run' THEN 1 ELSE 0 END) as not_run
            FROM executions e
            JOIN test_cases tc ON e.test_case_id = tc.id
            WHERE tc.suite_id = %s
        """
        return execute_query(query, (suite_id,), fetch_one=True)

    @staticmethod
    def get_stats_for_project(project_id):
        """Get execution stats for a project."""
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN e.result = 'Passed' THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN e.result = 'Failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN e.result = 'Blocked' THEN 1 ELSE 0 END) as blocked,
                SUM(CASE WHEN e.result = 'Not Run' THEN 1 ELSE 0 END) as not_run
            FROM executions e
            JOIN test_cases tc ON e.test_case_id = tc.id
            JOIN test_suites ts ON tc.suite_id = ts.id
            WHERE ts.project_id = %s
        """
        return execute_query(query, (project_id,), fetch_one=True)

    @staticmethod
    def get_trend(days=30):
        """Get execution trend over the last N days."""
        query = """
            SELECT date(execution_date) as exec_date,
                   SUM(CASE WHEN result = 'Passed' THEN 1 ELSE 0 END) as passed,
                   SUM(CASE WHEN result = 'Failed' THEN 1 ELSE 0 END) as failed,
                   SUM(CASE WHEN result = 'Blocked' THEN 1 ELSE 0 END) as blocked,
                   SUM(CASE WHEN result = 'Not Run' THEN 1 ELSE 0 END) as not_run
            FROM executions
            WHERE execution_date >= date('now', %s)
            GROUP BY date(execution_date)
            ORDER BY exec_date
        """
        return execute_query(query, (f'-{days} days',), fetch_all=True)

    @staticmethod
    def get_module_wise_stats():
        """Get pass percentage per module."""
        query = """
            SELECT tc.module,
                   COUNT(*) as total,
                   SUM(CASE WHEN e.result = 'Passed' THEN 1 ELSE 0 END) as passed,
                   ROUND(
                       CAST(SUM(CASE WHEN e.result = 'Passed' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 1
                   ) as pass_percentage
            FROM executions e
            JOIN test_cases tc ON e.test_case_id = tc.id
            WHERE tc.module != '' AND tc.module IS NOT NULL
            GROUP BY tc.module
            ORDER BY pass_percentage DESC
        """
        return execute_query(query, fetch_all=True)
