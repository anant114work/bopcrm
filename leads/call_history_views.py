import pandas as pd
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Lead, CallReportRecord, CallReportUpload
from django.db.models import Q
import re

def normalize_phone_number(phone):
    """Normalize phone number by removing all non-digit characters"""
    if not phone:
        return ""
    # Handle float format from Excel (e.g., 9876543210.0)
    phone_str = str(phone)
    if '.' in phone_str:
        phone_str = phone_str.split('.')[0]  # Remove decimal part
    return re.sub(r'\D', '', phone_str)

def match_phone_numbers(excel_phone, crm_phone):
    """
    Match phone numbers by comparing last 10 digits only
    """
    excel_clean = normalize_phone_number(excel_phone)
    crm_clean = normalize_phone_number(crm_phone)
    
    if not excel_clean or not crm_clean:
        return False, 0
    
    # Get last 10 digits for both numbers
    excel_last10 = excel_clean[-10:] if len(excel_clean) >= 10 else excel_clean
    crm_last10 = crm_clean[-10:] if len(crm_clean) >= 10 else crm_clean
    
    # Match only if last 10 digits are identical
    if excel_last10 == crm_last10 and len(excel_last10) >= 10:
        return True, 1  # Match found
    
    return False, 0

def call_history_upload(request):
    """Upload and process call history Excel file"""
    if request.method == 'POST':
        if 'excel_file' not in request.FILES:
            messages.error(request, 'Please select an Excel file to upload.')
            return redirect('call_history_upload')
        
        excel_file = request.FILES['excel_file']
        
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Please upload a valid Excel file (.xlsx or .xls)')
            return redirect('call_history_upload')
        
        try:
            # Read Excel file
            df = pd.read_excel(excel_file)
            
            # Check if required columns exist
            required_columns = ['Phone Number']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                messages.error(request, f'Missing required columns: {", ".join(missing_columns)}')
                return redirect('call_history_upload')
            
            # Process the data
            results = process_call_history_data(df)
            
            # Store results in session for display
            request.session['call_history_results'] = results
            messages.success(request, f'Successfully processed {len(results["matches"])} matches out of {len(df)} records.')
            
            return redirect('call_history_results')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('call_history_upload')
    
    return render(request, 'leads/call_history_upload.html')

def process_call_history_data(df):
    """Process call history data and match with CRM leads"""
    matches = []
    no_matches = []
    
    # Get all leads with phone numbers
    crm_leads = Lead.objects.exclude(phone_number__isnull=True).exclude(phone_number__exact='')
    
    for index, row in df.iterrows():
        excel_phone = str(row.get('Phone Number', '')).strip()
        
        if not excel_phone or excel_phone == 'nan':
            continue
        
        # Try to find matching lead
        best_match = None
        best_match_score = 0
        
        for lead in crm_leads:
            is_match, match_score = match_phone_numbers(excel_phone, lead.phone_number)
            
            if is_match and match_score > best_match_score:
                best_match = lead
                best_match_score = match_score
        
        # Prepare row data
        row_data = {
            'excel_phone': excel_phone,
            'match_score': best_match_score,
            'crm_lead': {
                'id': best_match.id,
                'full_name': best_match.full_name,
                'email': best_match.email,
                'phone_number': best_match.phone_number,
                'form_name': best_match.form_name
            } if best_match else None,
            'excel_data': {}
        }
        
        # Add all Excel columns to row data
        for col in df.columns:
            row_data['excel_data'][col] = str(row.get(col, '')) if pd.notna(row.get(col)) else ''
        
        if best_match:
            matches.append(row_data)
        else:
            no_matches.append(row_data)
    
    return {
        'matches': matches,
        'no_matches': no_matches,
        'total_processed': len(df)
    }

def call_history_results(request):
    """Display call history matching results"""
    import json
    
    results = request.session.get('call_history_results')
    
    if not results:
        messages.error(request, 'No results found. Please upload a file first.')
        return redirect('call_history_upload')
    
    # Ensure results have proper structure
    if not isinstance(results, dict):
        results = {'matches': [], 'no_matches': [], 'total_processed': 0}
    
    matches = results.get('matches', [])
    no_matches = results.get('no_matches', [])
    
    context = {
        'results': {
            'matches': json.dumps(matches),
            'no_matches': json.dumps(no_matches),
            'total_processed': results.get('total_processed', 0)
        },
        'matches': matches,
        'no_matches': no_matches,
        'matches_count': len(matches),
        'no_matches_count': len(no_matches),
        'total_processed': results.get('total_processed', 0)
    }
    
    return render(request, 'leads/call_history_results.html', context)

def save_call_history_matches(request):
    """Save matched call history data to CRM"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    results = request.session.get('call_history_results')
    if not results:
        return JsonResponse({'success': False, 'error': 'No results found'})
    
    try:
        # Create a new CallReportUpload record
        upload_record = CallReportUpload.objects.create(
            filename='call_history_import.xlsx',
            total_records=results['total_processed'],
            matched_records=len(results['matches']),
            unmatched_records=len(results['no_matches'])
        )
        
        saved_count = 0
        
        # Save matched records
        for match in results['matches']:
            try:
                # Get the actual Lead object
                lead_obj = Lead.objects.get(id=match['crm_lead']['id']) if match['crm_lead'] else None
                
                # Create CallReportRecord
                call_record = CallReportRecord.objects.create(
                    upload=upload_record,
                    matched_lead=lead_obj,
                    phone_number=match['excel_phone'],
                    call_date=match['excel_data'].get('Call Date', ''),
                    call_time=match['excel_data'].get('Call Time', ''),
                    call_duration=match['excel_data'].get('Call Duration', ''),
                    disposition=match['excel_data'].get('Disposition', ''),
                    agent=match['excel_data'].get('Agent', ''),
                    call_recording=match['excel_data'].get('Call Recording', ''),
                    call_transcript=match['excel_data'].get('Call Transcript', ''),
                    hangup_reason=match['excel_data'].get('Hangup Reason', ''),
                    cost=match['excel_data'].get('Cost', ''),
                    source=match['excel_data'].get('source', ''),
                    campaign_type=match['excel_data'].get('campaign_type', ''),
                    conversion_status=match['excel_data'].get('conversion_status', ''),
                    raw_data=match['excel_data']
                )
                
                # Create note with call details
                note_text = f"Call Record Added:\n"
                note_text += f"Date: {match['excel_data'].get('Call Date', 'N/A')}\n"
                note_text += f"Agent: {match['excel_data'].get('Agent', 'N/A')}\n"
                note_text += f"Duration: {match['excel_data'].get('Call Duration', 'N/A')}\n"
                note_text += f"Disposition: {match['excel_data'].get('Disposition', 'N/A')}\n"
                
                if match['excel_data'].get('Call Recording'):
                    note_text += f"Recording: {match['excel_data'].get('Call Recording')}\n"
                
                if match['excel_data'].get('Call Transcript'):
                    note_text += f"Transcript: {match['excel_data'].get('Call Transcript')[:200]}..."
                
                # Create system note
                from .models import LeadNote, TeamMember
                try:
                    system_user = TeamMember.objects.filter(name='System').first()
                    if not system_user:
                        system_user = TeamMember.objects.first()
                    
                    if system_user:
                        LeadNote.objects.create(
                            lead=lead_obj,
                            team_member=system_user,
                            note=note_text
                        )
                except Exception as note_error:
                    print(f"Error creating note: {note_error}")
                    pass
                
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving record: {e}")
                continue
        
        # Clear session data
        if 'call_history_results' in request.session:
            del request.session['call_history_results']
        
        return JsonResponse({
            'success': True, 
            'saved_count': saved_count,
            'upload_id': upload_record.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def call_history_dashboard(request):
    """Dashboard to view all call history uploads"""
    uploads = CallReportUpload.objects.all().order_by('-uploaded_at')
    
    context = {
        'uploads': uploads
    }
    
    return render(request, 'leads/call_history_dashboard.html', context)

def call_history_detail(request, upload_id):
    """View details of a specific call history upload"""
    try:
        upload = CallReportUpload.objects.get(id=upload_id)
        records = CallReportRecord.objects.filter(upload=upload).select_related('lead')
        
        context = {
            'upload': upload,
            'records': records
        }
        
        return render(request, 'leads/call_history_detail.html', context)
        
    except CallReportUpload.DoesNotExist:
        messages.error(request, 'Upload record not found.')
        return redirect('call_history_dashboard')