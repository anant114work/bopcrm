import requests
import csv
import io

SPREADSHEET_ID = '1uVTBtof0SWsJQaaioi-7b9uo4EL7s78gtelQpp9MyNY'

csv_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0'
response = requests.get(csv_url)

print(f"Status Code: {response.status_code}")
print(f"\nFirst 2000 characters of response:")
print("="*60)
print(response.text[:2000])
print("="*60)

if response.status_code == 200:
    csv_data = csv.DictReader(io.StringIO(response.text))
    print(f"\nColumn Headers: {csv_data.fieldnames}")
    
    print(f"\nFirst 5 rows:")
    for i, row in enumerate(csv_data):
        if i >= 5:
            break
        print(f"\nRow {i+1}:")
        for key, value in row.items():
            print(f"  {key}: {value}")
