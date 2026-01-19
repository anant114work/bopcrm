from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import csv
import io
import re
from datetime import datetime
import pytz
from django.utils import timezone
from leads.models import Lead, GoogleSheet

def extract_sheet_id(url):
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else None

@csrf_exempt
def sync_all_google_sheets(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    
    try:
        sheets = GoogleSheet.objects.filter(is_active=True)
        
        if not sheets.exists():
            return JsonResponse({'success': False, 'error': 'No active Google Sheets configured'})
        
        total_success = 0
        total_duplicate = 0
        sheets_synced = 0
        
        for sheet in sheets:
            try:
                spreadsheet_id = extract_sheet_id(sheet.sheet_url)
                if not spreadsheet_id:
                    continue
                
                csv_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=0'
                response = requests.get(csv_url, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                csv_data = csv.DictReader(io.StringIO(response.text))
                
                success = 0
                duplicate = 0
                
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
                        
                        lead_id = f"GS_{sheet.name[:10]}_{created.strftime('%Y%m%d_%H%M%S')}_{phone[-4:]}"
                        
                        Lead.objects.create(
                            lead_id=lead_id,
                            full_name=name,
                            phone_number=f"+91{phone}",
                            email=email,
                            configuration=unit_size,
                            form_name=f"Google Sheets - {project or sheet.name}",
                            source='Google Sheets',
                            created_time=created,
                            extra_fields={
                                'unit_size': unit_size,
                                'project_name': project or sheet.name,
                                'original_timestamp': timestamp,
                                'sheet_name': sheet.name
                            }
                        )
                        
                        success += 1
                        
                    except Exception as e:
                        continue
                
                if success > 0 or duplicate > 0:
                    total_success += success
                    total_duplicate += duplicate
                    sheets_synced += 1
                    sheet.last_synced = timezone.now()
                    sheet.save()
                    
            except Exception as e:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Synced {sheets_synced} sheets: {total_success} new leads, {total_duplicate} duplicates',
            'synced': total_success,
            'duplicates': total_duplicate,
            'sheets_synced': sheets_synced
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
