"""
Export Utility
Handles CSV and Excel export functionality.
"""

import csv
import io
from openpyxl import Workbook
from flask import make_response


def export_to_csv(data, headers, filename='export.csv'):
    """Export data to CSV and return as Flask response."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in data:
        writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def export_to_excel(data, headers, filename='export.xlsx', sheet_name='Report'):
    """Export data to Excel and return as Flask response."""
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    # Write headers
    ws.append(headers)

    # Style headers
    for cell in ws[1]:
        cell.font = cell.font.copy(bold=True)

    # Write data
    for row in data:
        ws.append(row)

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except (TypeError, AttributeError):
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response
