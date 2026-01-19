import requests

# The sheet ID you provided in the data
SPREADSHEET_ID = '1uVTBtof0SWsJQaaioi-7b9uo4EL7s78gtelQpp9MyNY'

print("Checking different sheet tabs (gid)...")
print("="*60)

# Try different gid values (sheet tabs)
for gid in range(0, 5):
    csv_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={gid}'
    response = requests.get(csv_url)
    
    print(f"\nGID {gid}: Status {response.status_code}")
    if response.status_code == 200:
        lines = response.text.split('\n')[:3]
        print(f"First 3 lines:")
        for line in lines:
            print(f"  {line[:150]}")
    print("-"*60)
