import os
import django
import requests
import csv
import io
from datetime import datetime
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from django.utils import timezone

SPREADSHEET_ID = '1uVTBtof0SWsJQaaioi-7b9uo4EL7s78gtelQpp9MyNY'

def sync_google_sheet_leads():
    """Sync all leads from Google Sheet"""
    try:
        csv_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0'
        response = requests.get(csv_url)
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch Google Sheet: {response.status_code}")
            return
        
        csv_reader = csv.reader(io.StringIO(response.text))
        
        success_count = 0
        duplicate_count = 0
        error_count = 0
        
        for row in csv_reader:
            try:
                if not row or len(row) < 3:
                    continue
                
                timestamp_str = row[0].strip() if len(row) > 0 else ''
                name = row[1].strip() if len(row) > 1 else ''
                phone = row[2].strip() if len(row) > 2 else ''
                email = row[3].strip() if len(row) > 3 else ''
                unit_size = row[4].strip() if len(row) > 4 else ''
                project_name = row[5].strip() if len(row) > 5 else 'Google Sheets Lead'
                
                if not name or not phone:
                    continue
                
                phone = phone.replace('+', '').replace(' ', '').replace('-', '')
                if len(phone) > 10:
                    phone = phone[-10:]
                
                phone_variants = [phone, f"+91{phone}", f"91{phone}"]
                
                existing_lead = Lead.objects.filter(phone_number__in=phone_variants).first()
                if existing_lead:
                    duplicate_count += 1
                    continue
                
                ist = pytz.timezone('Asia/Kolkata')
                try:
                    if '/' in timestamp_str and ':' in timestamp_str:
                        dt = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')
                        created_time = ist.localize(dt)
                    elif '/' in timestamp_str:
                        dt = datetime.strptime(timestamp_str, '%d/%m/%Y')
                        created_time = ist.localize(dt)
                    else:
                        created_time = timezone.now()
                except:
                    created_time = timezone.now()
                
                lead_id = f"GS_{created_time.strftime('%Y%m%d_%H%M%S')}_{phone[-4:]}"
                
                Lead.objects.create(
                    lead_id=lead_id,
                    full_name=name,
                    phone_number=f"+91{phone}",
                    email=email,
                    configuration=unit_size,
                    form_name=f"Google Sheets - {project_name}",
                    source='Google Sheets',
                    created_time=created_time,
                    extra_fields={
                        'unit_size': unit_size,
                        'project_name': project_name,
                        'original_timestamp': timestamp_str
                    }
                )
                
                success_count += 1
                print(f"[OK] {name} ({phone}) - {project_name}")
                
            except Exception as e:
                error_count += 1
                print(f"[ERROR] {str(e)}")
                continue
        
        print(f"\n{'='*60}")
        print(f"[SUCCESS] Created: {success_count} leads")
        print(f"[SKIP] Duplicates: {duplicate_count} leads")
        print(f"[ERROR] Errors: {error_count} leads")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"[FATAL] {str(e)}")

if __name__ == '__main__':
    print("Starting Google Sheets sync...")
    sync_google_sheet_leads()
