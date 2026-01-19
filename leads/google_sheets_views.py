from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from .models import Lead, GoogleSheet
import json
import requests

def google_sheets_dashboard(request):
    """Google Sheets integration dashboard"""
    sheets = GoogleSheet.objects.all().order_by('-created_at')
    
    # Get recent Google leads
    google_leads = Lead.objects.filter(
        lead_id__startswith='GS_'
    ).order_by('-created_time')[:10]
    
    context = {
        'sheets': sheets,
        'google_leads': google_leads,
        'total_google_leads': Lead.objects.filter(lead_id__startswith='GS_').count()
    }
    return render(request, 'leads/google_sheets_dashboard.html', context)

@csrf_exempt
def google_sheets_webhook(request):
    """Webhook to receive leads from Google Sheets"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Extract lead data
            name = data.get('name', '').strip()
            phone = data.get('phone', '').strip()
            email = data.get('email', '').strip()
            unit_size = data.get('unit_size', '').strip()
            project_name = data.get('project_name', 'Google Sheets Lead')
            ip_address = data.get('ip', '')
            timestamp = data.get('timestamp', '')
            
            # Parse the timestamp if provided
            from datetime import datetime
            import pytz
            
            created_time = timezone.now()  # Default to now
            if timestamp:
                try:
                    # Try to parse DD/MM/YYYY HH:MM:SS format
                    if '/' in timestamp and ':' in timestamp:
                        dt = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
                        ist = pytz.timezone('Asia/Kolkata')
                        created_time = ist.localize(dt)
                    # Try to parse DD/MM/YYYY format
                    elif '/' in timestamp:
                        dt = datetime.strptime(timestamp, '%d/%m/%Y')
                        ist = pytz.timezone('Asia/Kolkata')
                        created_time = ist.localize(dt)
                except Exception as e:
                    print(f"Error parsing timestamp {timestamp}: {e}")
                    # Keep default created_time
            
            # Normalize phone number for checking
            normalized_phone = phone.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
            if len(normalized_phone) == 10:
                normalized_phone = f"+91{normalized_phone}"
            elif len(normalized_phone) == 12 and normalized_phone.startswith('91'):
                normalized_phone = f"+{normalized_phone}"
            
            # Check multiple phone formats
            phone_variants = [
                phone,
                normalized_phone,
                normalized_phone.replace('+91', ''),
                normalized_phone.replace('+', '')
            ]
            
            existing_lead = Lead.objects.filter(phone_number__in=phone_variants).first()
            if existing_lead:
                print(f"Lead already exists: {name} ({phone}) - Skipping")
                return JsonResponse({
                    'success': True,
                    'message': 'Lead already exists',
                    'lead_id': existing_lead.id,
                    'duplicate': True
                })
            
            # Generate unique lead ID
            lead_id = f"GS_{timezone.now().strftime('%Y%m%d_%H%M%S')}_{phone[-4:]}"
            
            # Create lead with correct timestamp
            lead = Lead.objects.create(
                lead_id=lead_id,
                full_name=name,
                phone_number=phone,
                email=email,
                configuration=unit_size,
                form_name=f"Google Sheets - {project_name}",
                source='Google Sheets',
                created_time=created_time,
                extra_fields={
                    'ip_address': ip_address,
                    'original_timestamp': timestamp,
                    'unit_size': unit_size,
                    'project_name': project_name
                }
            )
            
            print(f"Google Sheets Lead Created: {name} ({phone}) - {project_name} - Date: {created_time.strftime('%d/%m/%Y %H:%M:%S')}")
            
            return JsonResponse({
                'success': True,
                'message': 'Lead created successfully',
                'lead_id': lead.id
            })
            
        except Exception as e:
            print(f"Google Sheets Webhook Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def add_google_sheet(request):
    """Add new Google Sheet configuration"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            sheet_url = request.POST.get('sheet_url')
            sheet_name = request.POST.get('sheet_name', 'Sheet1')
            
            if not name or not sheet_url:
                messages.error(request, 'Name and Sheet URL are required')
                return redirect('google_sheets_dashboard')
            
            GoogleSheet.objects.create(
                name=name,
                sheet_url=sheet_url,
                sheet_name=sheet_name
            )
            
            messages.success(request, f'Google Sheet "{name}" added successfully')
            
        except Exception as e:
            messages.error(request, f'Error adding sheet: {str(e)}')
    
    from django.shortcuts import redirect
    return redirect('google_sheets_dashboard')

@csrf_exempt
def test_google_sheets_webhook(request):
    """Test the Google Sheets webhook with sample data"""
    if request.method == 'POST':
        try:
            # Sample test data
            test_data = {
                'name': 'Test User',
                'phone': '9999999999',
                'email': 'test@example.com',
                'unit_size': '2 BHK',
                'project_name': 'AU Aspire Test',
                'ip': '192.168.1.1',
                'timestamp': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
            # Call our own webhook
            response = requests.post(
                request.build_absolute_uri('/google-sheets-webhook/'),
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return JsonResponse({
                    'success': True,
                    'message': 'Test webhook successful',
                    'response': response.json()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Webhook test failed: {response.text}'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def sync_existing_google_leads(request):
    """Manually sync existing Google Sheet leads to CRM"""
    if request.method == 'POST':
        try:
            # Sample leads from your Google Sheet data
            sample_leads = [
                {'name': 'Anil Kumar', 'phone': '7015837345', 'email': 'anilparbhuwala1@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Satya pramanik', 'phone': '8130118019', 'email': 'satyapramaniksmb@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Chinedu onyekelu', 'phone': '9863543954', 'email': 'chineduonyekelu0@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Praveen Kumar', 'phone': '7042628066', 'email': 'pkhdfc0439@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Subhashu', 'phone': '9810890895', 'email': '', 'project_name': 'Aspire Leisure Valley'},
            ]
            
            success_count = 0
            duplicate_count = 0
            
            for lead_data in sample_leads:
                try:
                    # Normalize phone number for checking
                    phone = lead_data['phone']
                    normalized_phone = phone.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
                    if len(normalized_phone) == 10:
                        normalized_phone = f"+91{normalized_phone}"
                    elif len(normalized_phone) == 12 and normalized_phone.startswith('91'):
                        normalized_phone = f"+{normalized_phone}"
                    
                    # Check multiple phone formats
                    phone_variants = [
                        phone,
                        normalized_phone,
                        normalized_phone.replace('+91', ''),
                        normalized_phone.replace('+', '')
                    ]
                    
                    existing_lead = Lead.objects.filter(phone_number__in=phone_variants).first()
                    if existing_lead:
                        print(f"⚠️ Lead already exists: {lead_data['name']} ({phone}) - Skipping")
                        duplicate_count += 1
                        continue
                    
                    # Generate unique lead ID
                    lead_id = f"GS_{timezone.now().strftime('%Y%m%d_%H%M%S')}_{lead_data['phone'][-4:]}"
                    
                    # Create lead
                    lead = Lead.objects.create(
                        lead_id=lead_id,
                        full_name=lead_data['name'],
                        phone_number=lead_data['phone'],
                        email=lead_data['email'],
                        form_name=f"Google Sheets - {lead_data['project_name']}",
                        source='Google Sheets',
                        created_time=timezone.now(),
                        extra_fields={
                            'project_name': lead_data['project_name'],
                            'synced_from': 'manual_sync'
                        }
                    )
                    success_count += 1
                    print(f"✅ Created new lead: {lead_data['name']} ({lead_data['phone']})")
                    
                except Exception as e:
                    print(f"Error creating lead {lead_data['name']}: {str(e)}")
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f'Synced {success_count} new leads, {duplicate_count} duplicates skipped',
                'synced_count': success_count,
                'duplicate_count': duplicate_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def sync_individual_sheet(request, sheet_id):
    """Sync a specific Google Sheet individually"""
    if request.method == 'POST':
        try:
            sheet = get_object_or_404(GoogleSheet, id=sheet_id)
            
            # In a real implementation, you would:
            # 1. Connect to Google Sheets API using sheet.sheet_url
            # 2. Read data from the specific sheet tab (sheet.sheet_name)
            # 3. Process each row and create leads
            
            # For now, simulate sync with sample data
            sample_leads = [
                {
                    'name': f'Sample Lead {sheet.name}',
                    'phone': f'9{sheet.id}00000000',
                    'email': f'sample{sheet.id}@example.com',
                    'project_name': sheet.name
                }
            ]
            
            success_count = 0
            duplicate_count = 0
            
            for lead_data in sample_leads:
                try:
                    # Check for duplicates
                    phone = lead_data['phone']
                    existing_lead = Lead.objects.filter(phone_number=phone).first()
                    
                    if existing_lead:
                        duplicate_count += 1
                        continue
                    
                    # Create lead
                    lead_id = f"GS_{sheet.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    Lead.objects.create(
                        lead_id=lead_id,
                        full_name=lead_data['name'],
                        phone_number=lead_data['phone'],
                        email=lead_data['email'],
                        form_name=f"Google Sheets - {sheet.name}",
                        source='Google Sheets',
                        created_time=timezone.now(),
                        extra_fields={
                            'sheet_id': sheet.id,
                            'sheet_name': sheet.name,
                            'project_name': lead_data['project_name']
                        }
                    )
                    success_count += 1
                    
                except Exception as e:
                    print(f"Error creating lead from {sheet.name}: {str(e)}")
                    continue
            
            # Update last synced time
            sheet.last_synced = timezone.now()
            sheet.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Sheet "{sheet.name}" synced: {success_count} new leads, {duplicate_count} duplicates',
                'synced_count': success_count,
                'duplicate_count': duplicate_count,
                'sheet_name': sheet.name
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def toggle_sheet_status(request, sheet_id):
    """Toggle active/inactive status of a Google Sheet"""
    if request.method == 'POST':
        try:
            sheet = get_object_or_404(GoogleSheet, id=sheet_id)
            sheet.is_active = not sheet.is_active
            sheet.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Sheet "{sheet.name}" is now {"active" if sheet.is_active else "inactive"}',
                'is_active': sheet.is_active
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_google_sheet(request, sheet_id):
    """Delete a Google Sheet configuration"""
    if request.method == 'POST':
        try:
            sheet = get_object_or_404(GoogleSheet, id=sheet_id)
            sheet_name = sheet.name
            sheet.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Sheet "{sheet_name}" deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})