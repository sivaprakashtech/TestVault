"""
Report Service
Centralized analytics queries for the Reports & Analytics module.
All queries are SQLite-compatible.
"""

from app.utils.database import execute_query


class ReportService:
    """Provides all analytics data for the reports module."""

    # --- SECTION 1: Summary Stats ---

    @staticmethod
    def get_summary():
        """Get overall summary counts."""
        queries = {
            'total_projects': "SELECT COUNT(*) as c FROM projects",
            'total_suites': "SELECT COUNT(*) as c FROM test_suites",
            'total_cases': "SELECT COUNT(*) as c FROM test_cases",
            'total_executions': "SELECT COUNT(*) as c FROM executions",
            'total_bugs': "SELECT COUNT(*) as c FROM bugs",
            'open_bugs': "SELECT COUNT(*) as c FROM bugs WHERE status IN ('Open', 'In Progress', 'Retest')",
            'closed_bugs': "SELECT COUNT(*) as c FROM bugs WHERE status = 'Closed'",
        }
        summary = {}
        for key, q in queries.items():
            r = execute_query(q, fetch_one=True)
            summary[key] = r['c'] if r else 0

        # Pass/Fail rates
        exec_stats = execute_query("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN result='Passed' THEN 1 ELSE 0 END) as passed,
                   SUM(CASE WHEN result='Failed' THEN 1 ELSE 0 END) as failed
            FROM executions
        """, fetch_one=True)
        total_exec = exec_stats['total'] if exec_stats else 0
        summary['pass_rate'] = round((exec_stats['passed'] or 0) / total_exec * 100, 1) if total_exec else 0
        summary['fail_rate'] = round((exec_stats['failed'] or 0) / total_exec * 100, 1) if total_exec else 0
        return summary

    # --- SECTION 2: Distribution Charts ---

    @staticmethod
    def get_execution_distribution():
        """Execution results distribution."""
        query = """
            SELECT result, COUNT(*) as count FROM executions GROUP BY result ORDER BY count DESC
        """
        return execute_query(query, fetch_all=True) or []

    @staticmethod
    def get_bug_severity_distribution():
        """Bug count by severity."""
        query = "SELECT severity, COUNT(*) as count FROM bugs GROUP BY severity ORDER BY count DESC"
        return execute_query(query, fetch_all=True) or []

    @staticmethod
    def get_bug_status_distribution():
        """Bug count by status."""
        query = "SELECT status, COUNT(*) as count FROM bugs GROUP BY status ORDER BY count DESC"
        return execute_query(query, fetch_all=True) or []

    @staticmethod
    def get_case_priority_distribution():
        """Test case priority distribution."""
        query = "SELECT priority, COUNT(*) as count FROM test_cases GROUP BY priority ORDER BY count DESC"
        return execute_query(query, fetch_all=True) or []

    # --- SECTION 3: Trends ---

    @staticmethod
    def get_execution_trend(days=30):
        """Executions per day for the last N days."""
        query = """
            SELECT date(execution_date) as day,
                   COUNT(*) as total,
                   SUM(CASE WHEN result='Passed' THEN 1 ELSE 0 END) as passed,
                   SUM(CASE WHEN result='Failed' THEN 1 ELSE 0 END) as failed,
                   SUM(CASE WHEN result='Blocked' THEN 1 ELSE 0 END) as blocked
            FROM executions
            WHERE execution_date >= date('now', %s)
            GROUP BY date(execution_date)
            ORDER BY day
        """
        return execute_query(query, (f'-{days} days',), fetch_all=True) or []

    @staticmethod
    def get_bug_trend(days=30):
        """Bugs created per day."""
        query = """
            SELECT date(created_date) as day, COUNT(*) as count
            FROM bugs
            WHERE created_date >= date('now', %s)
            GROUP BY date(created_date)
            ORDER BY day
        """
        return execute_query(query, (f'-{days} days',), fetch_all=True) or []

    @staticmethod
    def get_bug_closed_trend(days=30):
        """Bugs closed per day."""
        query = """
            SELECT date(updated_date) as day, COUNT(*) as count
            FROM bugs
            WHERE status = 'Closed' AND updated_date >= date('now', %s)
            GROUP BY date(updated_date)
            ORDER BY day
        """
        return execute_query(query, (f'-{days} days',), fetch_all=True) or []

    @staticmethod
    def get_pass_rate_trend(days=30):
        """Pass rate per day."""
        query = """
            SELECT date(execution_date) as day,
                   ROUND(CAST(SUM(CASE WHEN result='Passed' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as rate
            FROM executions
            WHERE execution_date >= date('now', %s)
            GROUP BY date(execution_date)
            ORDER BY day
        """
        return execute_query(query, (f'-{days} days',), fetch_all=True) or []

    # --- SECTION 4: Project Reports ---

    @staticmethod
    def get_project_reports():
        """Per-project analytics."""
        query = """
            SELECT p.id, p.name, p.project_key,
                   (SELECT COUNT(*) FROM test_suites WHERE project_id=p.id) as suites,
                   (SELECT COUNT(*) FROM test_cases tc JOIN test_suites ts ON tc.suite_id=ts.id WHERE ts.project_id=p.id) as cases,
                   (SELECT COUNT(*) FROM executions e JOIN test_cases tc ON e.test_case_id=tc.id JOIN test_suites ts ON tc.suite_id=ts.id WHERE ts.project_id=p.id) as executions,
                   (SELECT COUNT(*) FROM executions e JOIN test_cases tc ON e.test_case_id=tc.id JOIN test_suites ts ON tc.suite_id=ts.id WHERE ts.project_id=p.id AND e.result='Passed') as passed,
                   (SELECT COUNT(*) FROM executions e JOIN test_cases tc ON e.test_case_id=tc.id JOIN test_suites ts ON tc.suite_id=ts.id WHERE ts.project_id=p.id AND e.result='Failed') as failed,
                   (SELECT COUNT(*) FROM executions e JOIN test_cases tc ON e.test_case_id=tc.id JOIN test_suites ts ON tc.suite_id=ts.id WHERE ts.project_id=p.id AND e.result='Blocked') as blocked,
                   (SELECT COUNT(*) FROM bug_execution_links bel JOIN test_cases tc ON bel.test_case_id=tc.id JOIN test_suites ts ON tc.suite_id=ts.id JOIN bugs b ON bel.bug_table_id=b.id WHERE ts.project_id=p.id AND b.status IN ('Open','In Progress','Retest')) as open_bugs,
                   (SELECT COUNT(*) FROM bug_execution_links bel JOIN test_cases tc ON bel.test_case_id=tc.id JOIN test_suites ts ON tc.suite_id=ts.id JOIN bugs b ON bel.bug_table_id=b.id WHERE ts.project_id=p.id AND b.status='Closed') as closed_bugs
            FROM projects p
            ORDER BY p.name
        """
        results = execute_query(query, fetch_all=True) or []
        for r in results:
            total = r['executions'] or 0
            r['pass_pct'] = round(r['passed'] / total * 100, 1) if total else 0
            r['fail_pct'] = round(r['failed'] / total * 100, 1) if total else 0
            r['blocked_pct'] = round(r['blocked'] / total * 100, 1) if total else 0
            # Health score: high pass rate + low open bugs + low critical bugs = high health
            pass_score = min(r['pass_pct'], 100)
            bug_penalty = min((r['open_bugs'] or 0) * 5, 40)
            r['health'] = max(round(pass_score - bug_penalty, 0), 0) if total else 0
        return results

    # --- SECTION 5: Tester Analytics ---

    @staticmethod
    def get_tester_analytics():
        """Per-tester execution stats."""
        query = """
            SELECT u.full_name as tester,
                   COUNT(*) as total,
                   SUM(CASE WHEN e.result='Passed' THEN 1 ELSE 0 END) as passed,
                   SUM(CASE WHEN e.result='Failed' THEN 1 ELSE 0 END) as failed,
                   SUM(CASE WHEN e.result='Blocked' THEN 1 ELSE 0 END) as blocked,
                   ROUND(CAST(SUM(CASE WHEN e.result='Passed' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as pass_rate
            FROM executions e
            JOIN users u ON e.executed_by = u.id
            GROUP BY e.executed_by
            ORDER BY total DESC
        """
        return execute_query(query, fetch_all=True) or []

    # --- SECTION 6: Bug Reports ---

    @staticmethod
    def get_critical_bugs(limit=5):
        """Top critical/high severity open bugs."""
        query = """
            SELECT b.bug_id, b.title, b.severity, b.priority, b.status, b.created_date
            FROM bugs b
            WHERE b.severity IN ('Critical', 'High') AND b.status NOT IN ('Closed', 'Rejected')
            ORDER BY CASE b.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 END, b.created_date DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch_all=True) or []

    @staticmethod
    def get_newest_bugs(limit=5):
        """Most recently created bugs."""
        query = """
            SELECT b.bug_id, b.title, b.severity, b.status, b.created_date
            FROM bugs b ORDER BY b.created_date DESC LIMIT %s
        """
        return execute_query(query, (limit,), fetch_all=True) or []

    @staticmethod
    def get_recently_closed_bugs(limit=5):
        """Recently closed bugs."""
        query = """
            SELECT b.bug_id, b.title, b.severity, b.updated_date
            FROM bugs b WHERE b.status = 'Closed'
            ORDER BY b.updated_date DESC LIMIT %s
        """
        return execute_query(query, (limit,), fetch_all=True) or []

    @staticmethod
    def get_most_active_modules():
        """Modules with most bugs."""
        query = """
            SELECT module, COUNT(*) as count
            FROM bugs WHERE module != '' AND module IS NOT NULL
            GROUP BY module ORDER BY count DESC LIMIT 8
        """
        return execute_query(query, fetch_all=True) or []

    # --- SECTION 7: Export Data ---

    @staticmethod
    def get_export_data(report_type='executions', filters=None):
        """Get data formatted for export."""
        if report_type == 'executions':
            query = """
                SELECT tc.test_id, tc.title, tc.module, tc.priority,
                       e.result, e.environment, e.build_version,
                       e.execution_date, u.full_name as executed_by, e.actual_result, e.comments
                FROM executions e
                JOIN test_cases tc ON e.test_case_id = tc.id
                LEFT JOIN users u ON e.executed_by = u.id
                ORDER BY e.execution_date DESC
            """
            results = execute_query(query, fetch_all=True) or []
            headers = ['Test ID', 'Title', 'Module', 'Priority', 'Result',
                       'Environment', 'Build', 'Date', 'Tester', 'Actual Result', 'Comments']
            data = [[r['test_id'], r['title'], r['module'] or '', r['priority'],
                     r['result'], r['environment'] or '', r['build_version'] or '',
                     r['execution_date'] or '', r['executed_by'] or '', r['actual_result'] or '',
                     r['comments'] or ''] for r in results]
            return headers, data

        elif report_type == 'bugs':
            query = """
                SELECT b.bug_id, b.title, b.severity, b.priority, b.status,
                       b.module, b.environment, b.build_version, b.created_date,
                       u.full_name as reporter
                FROM bugs b LEFT JOIN users u ON b.reported_by = u.id
                ORDER BY b.created_date DESC
            """
            results = execute_query(query, fetch_all=True) or []
            headers = ['Bug ID', 'Title', 'Severity', 'Priority', 'Status',
                       'Module', 'Environment', 'Build', 'Date', 'Reporter']
            data = [[r['bug_id'], r['title'], r['severity'], r['priority'],
                     r['status'], r['module'] or '', r['environment'] or '',
                     r['build_version'] or '', r['created_date'] or '',
                     r['reporter'] or ''] for r in results]
            return headers, data

        elif report_type == 'projects':
            projects = ReportService.get_project_reports()
            headers = ['Project', 'Key', 'Suites', 'Cases', 'Executions',
                       'Pass %', 'Fail %', 'Blocked %', 'Open Bugs', 'Closed Bugs', 'Health']
            data = [[p['name'], p['project_key'], p['suites'], p['cases'],
                     p['executions'], p['pass_pct'], p['fail_pct'], p['blocked_pct'],
                     p['open_bugs'], p['closed_bugs'], p['health']] for p in projects]
            return headers, data

        return [], []
