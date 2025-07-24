import xlsxwriter
import uuid

def write_excel(findings):
    filename = f"securityhub_report_{uuid.uuid4().hex}.xlsx"
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Findings")

    headers = ["Resource ID", "Title", "Description", "Severity", "Created At", "Current Status"]
    for col, head in enumerate(headers):
        worksheet.write(0, col, head)

    for i, f in enumerate(findings, start=1):
        worksheet.write(i, 0, f['resource'])
        worksheet.write(i, 1, f['title'])
        worksheet.write(i, 2, f['description'])
        worksheet.write(i, 3, f['severity'])
        worksheet.write(i, 4, f['created_at'])
        worksheet.write(i, 5, f['status'])

    workbook.close()
    return filename
