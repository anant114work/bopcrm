import pandas as pd
import csv
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from .bulk_call_models import BulkCallCampaign, BulkCallRecord
from .bulk_call_service import bulk_call_processor
from .bulk_call_models import BulkCallCampaign
from .auto_call_new_leads import auto_call_service

def bulk_call_upload(request):
    """Upload CSV/Excel for bulk calling"""
    from .callkaro_models import CallKaroAgent
    from .ai_calling_models import AICallingAgent
    
    campaigns = BulkCallCampaign.objects.all()
    callkaro_agents = CallKaroAgent.objects.filter(is_active=True)
    ai_agents = AICallingAgent.objects.filter(is_active=True)
    
    agents = list(callkaro_agents) + list(ai_agents)
    
    return render(request, 'leads/bulk_call_upload.html', {
        'campaigns': campaigns,
        'agents': agents
    })

@csrf_exempt
def process_bulk_call_file(request):
    """Process uploaded CSV/Excel file"""
    if request.method == 'POST':
        try:
            agent_id = request.POST.get('agent_id')
            uploaded_file = request.FILES.get('file')
            
            if not agent_id or not uploaded_file:
                return JsonResponse({'success': False, 'error': 'Missing agent or file'})
            
            # Auto-generate campaign name
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            campaign_name = f"Bulk Call Campaign {timestamp}"
            
            # Use AU Reality agent ID if not provided
            if not agent_id or agent_id in ['default_agent', 'sales_agent', 'property_agent']:
                agent_id = "69294d3d2cc1373b1f3a3972"  # AU Reality Agent
            
            # Create campaign
            campaign = BulkCallCampaign.objects.create(
                name=campaign_name,
                file_name=uploaded_file.name,
                status='pending',
                agent_id=agent_id
            )
            
            # Process file based on extension
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if file_extension == 'csv':
                data = process_csv_file(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                data = process_excel_file(uploaded_file)
            else:
                campaign.delete()
                return JsonResponse({'success': False, 'error': 'Unsupported file format. Use CSV or Excel.'})
            
            if not data['success']:
                campaign.delete()
                return JsonResponse({'success': False, 'error': data['error']})
            
            # Create call records
            records_created = 0
            for row in data['rows']:
                name = row.get('name', '').strip()
                phone = row.get('phone', '').strip()
                
                if phone:  # Only create if phone number exists
                    BulkCallRecord.objects.create(
                        campaign=campaign,
                        name=name or 'Unknown',
                        phone_number=phone,
                        status='pending'
                    )
                    records_created += 1
            
            # Update campaign totals
            campaign.total_numbers = records_created
            campaign.save()
            
            print(f"[BULK CALL UPLOAD] Created campaign '{campaign_name}' with {records_created} numbers")
            
            return JsonResponse({
                'success': True,
                'message': f'Campaign created with {records_created} numbers',
                'campaign_id': campaign.id,
                'total_numbers': records_created
            })
            
        except Exception as e:
            print(f"[BULK CALL UPLOAD] Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def process_csv_file(uploaded_file):
    """Process CSV file"""
    try:
        # Read CSV
        decoded_file = uploaded_file.read().decode('utf-8')
        csv_reader = csv.DictReader(decoded_file.splitlines())
        
        rows = []
        for row in csv_reader:
            # Try different column name variations
            name = (row.get('name') or row.get('Name') or 
                   row.get('full_name') or row.get('Full Name') or '').strip()
            
            phone = (row.get('phone') or row.get('Phone') or 
                    row.get('phone_number') or row.get('Phone Number') or 
                    row.get('mobile') or row.get('Mobile') or '').strip()
            
            if phone:  # Only add if phone exists
                rows.append({'name': name, 'phone': phone})
        
        return {'success': True, 'rows': rows}
        
    except Exception as e:
        return {'success': False, 'error': f'CSV processing error: {str(e)}'}

def process_excel_file(uploaded_file):
    """Process Excel file"""
    try:
        # Read Excel
        df = pd.read_excel(uploaded_file)
        
        # Convert column names to lowercase for easier matching
        df.columns = df.columns.str.lower()
        
        rows = []
        for _, row in df.iterrows():
            # Try different column name variations
            name = ''
            phone = ''
            
            # Find name column
            for col in ['name', 'full_name', 'customer_name', 'client_name']:
                if col in df.columns and pd.notna(row[col]):
                    name = str(row[col]).strip()
                    break
            
            # Find phone column
            for col in ['phone', 'phone_number', 'mobile', 'contact', 'number']:
                if col in df.columns and pd.notna(row[col]):
                    phone = str(row[col]).strip()
                    break
            
            if phone:  # Only add if phone exists
                rows.append({'name': name, 'phone': phone})
        
        return {'success': True, 'rows': rows}
        
    except Exception as e:
        return {'success': False, 'error': f'Excel processing error: {str(e)}'}

def bulk_call_dashboard(request, campaign_id):
    """Dashboard to monitor bulk call campaign"""
    campaign = get_object_or_404(BulkCallCampaign, id=campaign_id)
    call_records = campaign.call_records.all().order_by('id')
    
    # Statistics
    stats = {
        'total': campaign.total_numbers,
        'completed': campaign.completed_calls,
        'successful': campaign.successful_calls,
        'failed': campaign.failed_calls,
        'pending': campaign.total_numbers - campaign.completed_calls,
        'success_rate': (campaign.successful_calls / campaign.completed_calls * 100) if campaign.completed_calls > 0 else 0
    }
    
    return render(request, 'leads/bulk_call_dashboard.html', {
        'campaign': campaign,
        'call_records': call_records,
        'stats': stats
    })

@csrf_exempt
def start_bulk_calling(request, campaign_id):
    """Start the bulk calling process"""
    if request.method == 'POST':
        success, message = bulk_call_processor.start_campaign(campaign_id)
        return JsonResponse({'success': success, 'message': message})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def stop_bulk_calling(request, campaign_id):
    """Stop the bulk calling process"""
    if request.method == 'POST':
        success, message = bulk_call_processor.stop_campaign(campaign_id)
        return JsonResponse({'success': success, 'message': message})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def resume_bulk_calling(request, campaign_id):
    """Resume calling only pending numbers"""
    if request.method == 'POST':
        try:
            campaign = BulkCallCampaign.objects.get(id=campaign_id)
            
            # Count pending calls
            pending_count = campaign.call_records.filter(status='pending').count()
            
            if pending_count == 0:
                return JsonResponse({'success': False, 'message': 'No pending calls to resume'})
            
            # Start campaign (will automatically skip duplicates)
            success, message = bulk_call_processor.start_campaign(campaign_id)
            
            if success:
                return JsonResponse({
                    'success': True, 
                    'message': f'Resumed calling {pending_count} pending numbers'
                })
            else:
                return JsonResponse({'success': False, 'message': message})
                
        except BulkCallCampaign.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Campaign not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def bulk_call_status_api(request, campaign_id):
    """API to get real-time campaign status"""
    try:
        campaign = BulkCallCampaign.objects.get(id=campaign_id)
        
        # Get recent call records
        recent_calls = campaign.call_records.exclude(status='pending').order_by('-initiated_at')[:10]
        
        calls_data = []
        for call in recent_calls:
            calls_data.append({
                'name': call.name,
                'phone': call.phone_number,
                'status': call.status,
                'initiated_at': call.initiated_at.strftime('%H:%M:%S') if call.initiated_at else '',
                'duration': call.duration_seconds
            })
        
        return JsonResponse({
            'success': True,
            'campaign': {
                'name': campaign.name,
                'status': campaign.status,
                'total': campaign.total_numbers,
                'completed': campaign.completed_calls,
                'successful': campaign.successful_calls,
                'failed': campaign.failed_calls,
                'success_rate': (campaign.successful_calls / campaign.completed_calls * 100) if campaign.completed_calls > 0 else 0
            },
            'recent_calls': calls_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def cleanup_campaigns_api(request):
    """API to clean up inconsistent campaign states"""
    if request.method == 'POST':
        result = bulk_call_processor.cleanup_campaigns()
        return JsonResponse(result)
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def campaign_status_check(request, campaign_id):
    """Check specific campaign status and fix if needed"""
    try:
        status_info = bulk_call_processor.get_campaign_status(campaign_id)
        return JsonResponse(status_info)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def auto_call_new_leads(request):
    """Auto-call new leads from AU forms"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            since_minutes = data.get('since_minutes', 60)
            
            # Call new AU leads
            results = auto_call_service.call_au_forms_leads(since_minutes=since_minutes)
            
            return JsonResponse({
                'success': True,
                'message': f'Called {results["successful_calls"]} leads successfully, {results["failed_calls"]} failed',
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def get_new_leads_count(request):
    """Get count of new leads that can be auto-called"""
    try:
        since_minutes = int(request.GET.get('since_minutes', 60))
        
        new_leads = auto_call_service.get_new_leads_for_calling(
            form_names=[
                'AU without OTP form 06/12/2025, 16:48',
                'AU Leisure Valley form 18/11/2025, 15:11'
            ],
            since_minutes=since_minutes
        )
        
        return JsonResponse({
            'success': True,
            'count': new_leads.count(),
            'leads': [{
                'name': lead.full_name,
                'phone': lead.phone_number,
                'form': lead.form_name,
                'created': lead.created_time.strftime('%Y-%m-%d %H:%M:%S')
            } for lead in new_leads[:10]]  # Show first 10
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def delete_bulk_campaign(request, campaign_id):
    """Delete a bulk call campaign"""
    if request.method == 'POST':
        try:
            campaign = BulkCallCampaign.objects.get(id=campaign_id)
            campaign_name = campaign.name
            campaign.delete()
            return JsonResponse({
                'success': True,
                'message': f'Campaign "{campaign_name}" deleted successfully'
            })
        except BulkCallCampaign.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Campaign not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
