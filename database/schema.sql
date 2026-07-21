-- =====================================================
-- QA Test Management System - SQLite Schema
-- Version: 1.1 (SQLite)
-- =====================================================

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'QA Engineer' CHECK(role IN ('QA Engineer', 'Admin')),
    is_active INTEGER DEFAULT 1,
    last_login TEXT,
    created_date TEXT DEFAULT (datetime('now')),
    updated_date TEXT DEFAULT (datetime('now'))
);

-- Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    project_key TEXT NOT NULL UNIQUE,
    description TEXT,
    status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Archived')),
    created_by INTEGER,
    created_date TEXT DEFAULT (datetime('now')),
    updated_date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Test Suites Table
CREATE TABLE IF NOT EXISTS test_suites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'Medium' CHECK(priority IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Archived')),
    created_by INTEGER,
    created_date TEXT DEFAULT (datetime('now')),
    updated_date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Test Cases Table
CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT NOT NULL UNIQUE,
    suite_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    preconditions TEXT,
    steps TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    module TEXT,
    feature TEXT,
    priority TEXT NOT NULL DEFAULT 'Medium' CHECK(priority IN ('Critical', 'High', 'Medium', 'Low')),
    severity TEXT DEFAULT 'Major' CHECK(severity IN ('Blocker', 'Critical', 'Major', 'Minor', 'Trivial')),
    type TEXT DEFAULT 'Functional' CHECK(type IN ('Functional', 'Regression', 'Smoke', 'Sanity', 'API', 'UI')),
    status TEXT DEFAULT 'Draft' CHECK(status IN ('Draft', 'Ready', 'Active', 'Deprecated')),
    created_by INTEGER,
    created_date TEXT DEFAULT (datetime('now')),
    updated_date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Executions Table
CREATE TABLE IF NOT EXISTS executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id INTEGER NOT NULL,
    result TEXT NOT NULL CHECK(result IN ('Passed', 'Failed', 'Blocked', 'Not Run')),
    actual_result TEXT,
    executed_by INTEGER,
    execution_date TEXT DEFAULT (datetime('now')),
    environment TEXT DEFAULT 'QA' CHECK(environment IN ('QA', 'UAT', 'Production', 'Development', 'Staging')),
    build_version TEXT,
    duration INTEGER,
    comments TEXT,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (executed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Bugs Table
CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    steps_to_reproduce TEXT,
    expected_result TEXT,
    actual_result TEXT,
    severity TEXT DEFAULT 'Medium' CHECK(severity IN ('Critical', 'High', 'Medium', 'Low')),
    priority TEXT DEFAULT 'P2' CHECK(priority IN ('P1', 'P2', 'P3', 'P4')),
    status TEXT DEFAULT 'Open' CHECK(status IN ('Open', 'In Progress', 'Fixed', 'Retest', 'Closed', 'Rejected')),
    module TEXT,
    environment TEXT,
    build_version TEXT,
    assigned_to INTEGER,
    reported_by INTEGER,
    created_date TEXT DEFAULT (datetime('now')),
    updated_date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (reported_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Bug-Execution Links (junction table)
CREATE TABLE IF NOT EXISTS bug_execution_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_table_id INTEGER NOT NULL,
    execution_id INTEGER,
    test_case_id INTEGER NOT NULL,
    linked_by INTEGER,
    linked_date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (bug_table_id) REFERENCES bugs(id) ON DELETE CASCADE,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE SET NULL,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (linked_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Legacy bug_links table kept for backward compat
CREATE TABLE IF NOT EXISTS bug_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id INTEGER NOT NULL,
    bug_id TEXT NOT NULL,
    bug_title TEXT NOT NULL,
    bug_status TEXT NOT NULL,
    bug_priority TEXT NOT NULL,
    linked_by INTEGER,
    linked_date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (linked_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Attachments Table
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    original_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    uploaded_by INTEGER,
    uploaded_date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Activity Log Table
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action_type TEXT NOT NULL CHECK(action_type IN ('created', 'updated', 'deleted', 'executed', 'linked')),
    entity_type TEXT NOT NULL CHECK(entity_type IN ('project', 'suite', 'test_case', 'execution', 'bug_link')),
    entity_id INTEGER NOT NULL,
    description TEXT,
    created_date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_key ON projects(project_key);
CREATE INDEX IF NOT EXISTS idx_test_suites_project ON test_suites(project_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_suite ON test_cases(suite_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_module ON test_cases(module);
CREATE INDEX IF NOT EXISTS idx_test_cases_priority ON test_cases(priority);
CREATE INDEX IF NOT EXISTS idx_test_cases_test_id ON test_cases(test_id);
CREATE INDEX IF NOT EXISTS idx_executions_test_case ON executions(test_case_id);
CREATE INDEX IF NOT EXISTS idx_executions_date ON executions(execution_date);
CREATE INDEX IF NOT EXISTS idx_bug_links_test_case ON bug_links(test_case_id);
CREATE INDEX IF NOT EXISTS idx_bugs_status ON bugs(status);
CREATE INDEX IF NOT EXISTS idx_bugs_severity ON bugs(severity);
CREATE INDEX IF NOT EXISTS idx_bugs_bug_id ON bugs(bug_id);
CREATE INDEX IF NOT EXISTS idx_bug_exec_links_bug ON bug_execution_links(bug_table_id);
CREATE INDEX IF NOT EXISTS idx_bug_exec_links_case ON bug_execution_links(test_case_id);
