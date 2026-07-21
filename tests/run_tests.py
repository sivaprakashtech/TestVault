"""
Automated Test Runner
Uses test_database.db - NEVER touches production qa_test_management.db.

Usage: python tests/run_tests.py
"""

import os
import sys

# MUST be set before any app import
os.environ['TESTING'] = '1'

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from tests.conftest import setup_test_app, teardown_test_db, verify_production_db_untouched
from tests.conftest import TEST_DB_PATH, PROD_DB_PATH

# Record production DB state before tests
prod_existed_before = os.path.exists(PROD_DB_PATH)
prod_size_before = os.path.getsize(PROD_DB_PATH) if prod_existed_before else 0

print("=" * 60)
print("  AUTOMATED TESTS - Using test_database.db")
print(f"  Production DB: {'EXISTS' if prod_existed_before else 'NOT FOUND'} ({prod_size_before} bytes)")
print("=" * 60)

# Create test app
app = setup_test_app()
verify_production_db_untouched()
print(f"\n[SAFE] Test DB path: {TEST_DB_PATH}")
print(f"[SAFE] Production DB untouched: {PROD_DB_PATH}\n")

from app.models.user import User
from app.models.project import Project
from app.models.test_suite import TestSuite

# ===== AUTH TESTS =====
print("--- Auth Tests ---")
uid = User.create('Test User', 'test@example.com', 'password123')
assert uid is not None
print(f"[OK] Register: user created (id={uid})")

user = User.find_by_email('test@example.com')
assert user is not None
assert User.verify_password(user['password_hash'], 'password123')
print("[OK] Login: password verification passed")

# ===== PROJECT TESTS =====
print("\n--- Project Tests ---")
p1 = Project.create('Test Project', 'TPROJ', 'Description', uid)
assert p1 is not None
print(f"[OK] Create project (id={p1})")

project = Project.get_by_id(p1)
assert project['name'] == 'Test Project'
assert project['project_key'] == 'TPROJ'
print("[OK] Get project by ID")

Project.update(p1, 'Updated Project', 'UPROJ', 'New desc')
updated = Project.get_by_id(p1)
assert updated['name'] == 'Updated Project'
print("[OK] Update project")

result = Project.get_all(filters={'search': 'Updated'})
assert result['total'] == 1
print("[OK] Search project")

result = Project.get_all(page=1, per_page=5)
assert result['total'] == 1
print("[OK] Pagination")

# ===== TEST SUITE TESTS =====
print("\n--- Test Suite Tests ---")
s1 = TestSuite.create(p1, 'Suite One', 'Description', 'High', uid)
s2 = TestSuite.create(p1, 'Suite Two', 'Another', 'Medium', uid)
assert s1 is not None
print(f"[OK] Create suites (ids={s1},{s2})")

suite = TestSuite.get_by_id(s1)
assert suite['name'] == 'Suite One'
assert suite['priority'] == 'High'
print("[OK] Get suite by ID")

TestSuite.update(s1, 'Suite Updated', 'New desc', 'Critical')
updated = TestSuite.get_by_id(s1)
assert updated['name'] == 'Suite Updated'
assert updated['priority'] == 'Critical'
print("[OK] Update suite")

TestSuite.archive(s2)
suite2 = TestSuite.get_by_id(s2)
assert suite2['status'] == 'Archived'
print("[OK] Archive suite")

TestSuite.activate(s2)
suite2 = TestSuite.get_by_id(s2)
assert suite2['status'] == 'Active'
print("[OK] Activate suite")

result = TestSuite.get_by_project(p1, filters={'search': 'Updated'})
assert result['total'] == 1
print("[OK] Search suite")

TestSuite.delete(s2)
result = TestSuite.get_by_project(p1)
assert result['total'] == 1
print("[OK] Delete suite")

# ===== ROUTE TESTS =====
print("\n--- HTTP Route Tests ---")
with app.test_client() as c:
    c.post('/login', data={'email': 'test@example.com', 'password': 'password123'})

    r = c.get('/')
    assert r.status_code == 200
    print("[OK] Dashboard -> 200")

    r = c.get('/projects/')
    assert r.status_code == 200
    print("[OK] Projects list -> 200")

    r = c.post('/projects/create', data={
        'name': 'Route Project', 'project_key': 'RPROJ', 'description': ''
    }, follow_redirects=True)
    assert r.status_code == 200
    print("[OK] Create project via route -> 200")

    r = c.get(f'/suites/project/{p1}')
    assert r.status_code == 200
    print("[OK] Suites list -> 200")

    r = c.post(f'/suites/create/{p1}', data={
        'name': 'Route Suite', 'description': '', 'priority': 'High'
    }, follow_redirects=True)
    assert r.status_code == 200
    print("[OK] Create suite via route -> 200")

# ===== CLEANUP & VERIFICATION =====
print("\n--- Safety Verification ---")

# Verify production DB was NOT touched
verify_production_db_untouched()
prod_exists_after = os.path.exists(PROD_DB_PATH)
prod_size_after = os.path.getsize(PROD_DB_PATH) if prod_exists_after else 0

if prod_existed_before:
    assert prod_exists_after, "CRITICAL: Production DB was deleted!"
    assert prod_size_after == prod_size_before, "CRITICAL: Production DB was modified!"
    print(f"[SAFE] Production DB intact: {prod_size_after} bytes (unchanged)")
else:
    print(f"[SAFE] Production DB did not exist before, still doesn't: {prod_exists_after}")

# Clean up test DB
teardown_test_db()
assert not os.path.exists(TEST_DB_PATH), "Test DB should be deleted after tests"
print(f"[OK] Test DB cleaned up: {TEST_DB_PATH}")

print("\n" + "=" * 60)
print("  ALL TESTS PASSED - PRODUCTION DB SAFE")
print("=" * 60)
