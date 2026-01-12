import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Team Members"

border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

sample_data = [
    ["Tushar Bhatia", 7056145678],
    ["Abhishek Prajapati", 9044497237],
    ["Yukti Kashyap", 8512882615],
]

for row_num, row_data in enumerate(sample_data, 1):
    for col_num, value in enumerate(row_data, 1):
        cell = ws.cell(row=row_num, column=col_num)
        cell.value = value
        cell.border = border
        cell.alignment = Alignment(horizontal="left", vertical="center")

ws.column_dimensions['A'].width = 25
ws.column_dimensions['B'].width = 15

wb.save('d:\\AI-proto\\CRM\\drip\\static\\templates\\team_members_template.xlsx')
print("Template created")
