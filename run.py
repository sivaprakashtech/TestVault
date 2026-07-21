"""
QA Test Management System - Application Entry Point
A professional QA Test Management tool for managing test cases,
tracking executions, linking bugs, and generating reports.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
