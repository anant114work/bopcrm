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

SPREADSHEET_ID = '1tBO3sEET72uIJbdK2hixCCq4IicAv0eJxScWrnHzqMM'

def sync_spj_leads():
    try:
        csv_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0'
        response = requests.get(csv_url)
        
        if response.status_code != 200:
            print(f"[ERROR] Failed: {response.status_code}")
            return
        
        csv_data = csv.DictReader(io.StringIO(response.text))
        
        success = 0
        duplicate = 0
        error = 0
        
        for row in csv_data:
            try:
                name = row.get('Name', '').strip()
                phone = row.get('Phone', '').strip()
                email = row.get('Email', '').strip().replace('mailto:', '')
                unit_size = row.get('Unit Size', '').strip()
                project = row.get('Project Name', '').strip()
                timestamp = row.get('Date & Time', '').strip()
                
                if not name or not phone:
                    continue
                
                phone = phone.replace('+', '').replace(' ', '').replace('-', '')
                if len(phone) > 10:
                    phone = phone[-10:]
                
                variants = [phone, f"+91{phone}", f"91{phone}"]
                
                if Lead.objects.filter(phone_number__in=variants).exists():
                    duplicate += 1
                    continue
                
                ist = pytz.timezone('Asia/Kolkata')
                try:
                    if '/' in timestamp and ':' in timestamp:
                        dt = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
                        created = ist.localize(dt)
                    elif '/' in timestamp:
                        dt = datetime.strptime(timestamp, '%d/%m/%Y')
                        created = ist.localize(dt)
                    else:
                        created = timezone.now()
                except:
                    created = timezone.now()
                
                lead_id = f"GS_SPJ_{created.strftime('%Y%m%d_%H%M%S')}_{phone[-4:]}"
                
                Lead.objects.create(
                    lead_id=lead_id,
                    full_name=name,
                    phone_number=f"+91{phone}",
                    email=email,
                    configuration=unit_size,
                    form_name=f"Google Sheets - {project}",
                    source='Google Sheets',
                    created_time=created,
                    extra_fields={
                        'unit_size': unit_size,
                        'project_name': project,
                        'original_timestamp': timestamp
                    }
                )
                
                success += 1
                if success % 50 == 0:
                    print(f"[PROGRESS] {success} leads created...")
                
            except Exception as e:
                error += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"[SUCCESS] Created: {success}")
        print(f"[SKIP] Duplicates: {duplicate}")
        print(f"[ERROR] Errors: {error}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"[FATAL] {str(e)}")

if __name__ == '__main__':
    print("Syncing SPJ Google Sheet...")
    sync_spj_leads()
