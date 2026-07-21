-- =====================================================
-- QA Test Management System - Seed Data (SQLite)
-- For demonstration and testing purposes
-- Run AFTER registering a user via the app
-- =====================================================

-- Insert demo projects (assumes user ID 1 exists)
INSERT OR IGNORE INTO projects (name, description, created_by) VALUES
('E-Commerce Platform', 'Main e-commerce web application testing project', 1);
INSERT OR IGNORE INTO projects (name, description, created_by) VALUES
('Mobile Banking App', 'Banking mobile application QA project', 1);
INSERT OR IGNORE INTO projects (name, description, created_by) VALUES
('Healthcare Portal', 'Patient management system testing', 1);

-- Insert test suites
INSERT OR IGNORE INTO test_suites (project_id, name, description, created_by) VALUES
(1, 'Authentication Module', 'Login, Register, Password Reset tests', 1);
INSERT OR IGNORE INTO test_suites (project_id, name, description, created_by) VALUES
(1, 'Shopping Cart', 'Cart operations and checkout flow', 1);
INSERT OR IGNORE INTO test_suites (project_id, name, description, created_by) VALUES
(1, 'Payment Gateway', 'Payment processing and verification', 1);
INSERT OR IGNORE INTO test_suites (project_id, name, description, created_by) VALUES
(2, 'Login & Security', 'Authentication and security tests', 1);
INSERT OR IGNORE INTO test_suites (project_id, name, description, created_by) VALUES
(2, 'Fund Transfer', 'Money transfer functionality tests', 1);
INSERT OR IGNORE INTO test_suites (project_id, name, description, created_by) VALUES
(3, 'Patient Records', 'Patient data management tests', 1);

-- Insert test cases
INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0001', 1, 'Valid Login with Correct Credentials', 'Verify user can login with valid credentials', 'User account exists in the system', '1. Navigate to login page
2. Enter valid email
3. Enter valid password
4. Click Login button', 'User should be redirected to dashboard with success message', 'Authentication', 'Login', 'Critical', 'Blocker', 'Active', 1);

INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0002', 1, 'Invalid Login with Wrong Password', 'Verify error message for incorrect password', 'User account exists in the system', '1. Navigate to login page
2. Enter valid email
3. Enter incorrect password
4. Click Login button', 'Error message should appear: Invalid credentials', 'Authentication', 'Login', 'High', 'Critical', 'Active', 1);

INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0003', 1, 'Login with Empty Fields', 'Verify validation for empty fields', 'None', '1. Navigate to login page
2. Leave fields empty
3. Click Login button', 'Validation messages should appear for required fields', 'Authentication', 'Login', 'Medium', 'Major', 'Active', 1);

INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0004', 2, 'Add Product to Cart', 'Verify product can be added to shopping cart', 'User is logged in, product exists', '1. Navigate to product page
2. Select quantity
3. Click Add to Cart
4. View cart', 'Product should appear in cart with correct quantity and price', 'Shopping', 'Cart', 'Critical', 'Blocker', 'Active', 1);

INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0005', 2, 'Remove Product from Cart', 'Verify product removal from cart', 'Product exists in cart', '1. Navigate to cart
2. Click Remove on product
3. Confirm removal', 'Product should be removed, cart total updated', 'Shopping', 'Cart', 'High', 'Critical', 'Active', 1);

INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0006', 3, 'Process Credit Card Payment', 'Verify credit card payment processing', 'Items in cart, valid credit card', '1. Proceed to checkout
2. Select credit card
3. Enter card details
4. Click Pay Now', 'Payment should be processed, confirmation displayed', 'Payment', 'Credit Card', 'Critical', 'Blocker', 'Active', 1);

INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0007', 4, 'Biometric Login', 'Verify fingerprint authentication', 'Biometric data registered', '1. Open app
2. Place finger on sensor
3. Wait for authentication', 'User should be authenticated and logged in', 'Security', 'Biometric', 'High', 'Critical', 'Active', 1);

INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0008', 5, 'Transfer Between Own Accounts', 'Verify self-transfer functionality', 'User has multiple accounts with balance', '1. Select source account
2. Select destination account
3. Enter amount
4. Confirm transfer', 'Amount should be debited from source and credited to destination', 'Banking', 'Transfer', 'Critical', 'Blocker', 'Active', 1);

INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0009', 6, 'Create New Patient Record', 'Verify patient record creation', 'User has admin access', '1. Click New Patient
2. Fill required fields
3. Upload documents
4. Save record', 'Patient record should be created with unique ID', 'Records', 'Patient Management', 'High', 'Critical', 'Active', 1);

INSERT OR IGNORE INTO test_cases (test_id, suite_id, title, description, preconditions, steps, expected_result, module, feature, priority, severity, status, created_by) VALUES
('TC-0010', 6, 'Search Patient by ID', 'Verify patient search functionality', 'Patient records exist in system', '1. Navigate to search
2. Enter patient ID
3. Click Search', 'Patient details should be displayed', 'Records', 'Search', 'Medium', 'Major', 'Active', 1);

-- Insert execution records
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(1, 'Passed', 1, 'Login successful with correct credentials', 'Chrome 120 / Windows 11', 'v2.1.0');
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(2, 'Passed', 1, 'Error message displayed correctly', 'Chrome 120 / Windows 11', 'v2.1.0');
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(3, 'Passed', 1, 'Validation working as expected', 'Firefox 121 / macOS', 'v2.1.0');
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(4, 'Failed', 1, 'Cart total not updating after adding product', 'Chrome 120 / Windows 11', 'v2.1.0');
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(5, 'Passed', 1, 'Removal working correctly', 'Chrome 120 / Windows 11', 'v2.1.0');
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(6, 'Blocked', 1, 'Payment gateway sandbox is down', 'Chrome 120 / Windows 11', 'v2.1.0');
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(7, 'Passed', 1, 'Biometric authentication successful', 'Android 14 / Pixel 8', 'v1.5.0');
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(8, 'Failed', 1, 'Transfer fails for amounts above 50000', 'iOS 17 / iPhone 15', 'v1.5.0');
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(9, 'Passed', 1, 'Record created successfully', 'Chrome 120 / Windows 11', 'v3.0.0');
INSERT INTO executions (test_case_id, result, executed_by, notes, environment, build_version) VALUES
(10, 'Not Executed', 1, 'Skipped due to dependency on TC-0009', 'N/A', 'v3.0.0');

-- Insert bug links
INSERT INTO bug_links (test_case_id, bug_id, bug_title, bug_status, bug_priority, linked_by) VALUES
(4, 'BUG-1042', 'Cart total not recalculating on item add', 'Open', 'Critical', 1);
INSERT INTO bug_links (test_case_id, bug_id, bug_title, bug_status, bug_priority, linked_by) VALUES
(6, 'BUG-1038', 'Payment gateway timeout on sandbox environment', 'In Progress', 'High', 1);
INSERT INTO bug_links (test_case_id, bug_id, bug_title, bug_status, bug_priority, linked_by) VALUES
(8, 'BUG-1055', 'Transfer limit validation fails for high amounts', 'Open', 'Critical', 1);
