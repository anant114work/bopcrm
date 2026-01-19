from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db import models
from datetime import datetime
import pandas as pd
import io
from .call_report_models import CallReportUpload, CallReportRecord

def call_report_upload_page(request):
    """Page to upload call reports"""
    recent_uploads = CallReportUpload.objects.all()[:10]
    
    context = {
        'recent_uploads': recent_uploads
    }
    return render(request, 'leads/call_report_upload.html', context)

@csrf_exempt
def process_call_report_upload(request):
    """Process uploaded Excel file and match with call logs"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'})
    
    if 'excel_file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No file uploaded'})
    
    excel_file = request.FILES['excel_file']
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        # Create upload record
        upload = CallReportUpload.objects.create(
            filename=excel_file.name,
            total_records=len(df)
        )
        
        matched_count = 0
        unmatched_count = 0
        
        for _, row in df.iterrows():
            try:
                # Parse call time
                call_time = None
                if pd.notna(row.get('Call Time')):
                    try:
                        call_time = pd.to_datetime(row['Call Time'])
                    except:
                        pass
                
                # Parse call date
                call_date = None
                if pd.notna(row.get('Call Date')):
                    try:
                        call_date = pd.to_datetime(row['Call Date']).date()
                    except:
                        pass
                
                # Simple phone number extraction
                phone = str(row.get('Phone Number', '')).strip()
                phone_variants = []
                
                if phone and phone != 'nan':
                    # Extract all digits
                    digits_only = ''.join(filter(str.isdigit, phone))
                    
                    if len(digits_only) >= 10:
                        # Get last 10 digits
                        last_10 = digits_only[-10:]
                        phone_variants = [digits_only, last_10, f"+91{last_10}", f"91{last_10}"]
                    else:
                        phone_variants = [digits_only]
                
                # Create call report record
                record = CallReportRecord.objects.create(
                    upload=upload,
                    phone_number=phone,
                    agent=str(row.get('Agent', '')),
                    version=str(row.get('Version', '')),
                    call_date=call_date,
                    call_time=call_time,
                    disposition=str(row.get('Disposition', '')),
                    call_duration=float(row.get('Call Duration', 0)) if pd.notna(row.get('Call Duration')) else None,
                    call_recording=str(row.get('Call Recording', '')),
                    try_count=int(row.get('Try Count', 0)) if pd.notna(row.get('Try Count')) else 0,
                    hangup_reason=str(row.get('Hangup Reason', '')),
                    cost=float(row.get('Cost', 0)) if pd.notna(row.get('Cost')) else None,
                    source=str(row.get('source', '')),
                    project=str(row.get('project', '')),
                    campaign_type=str(row.get('campaign_type', '')),
                    lead_source=str(row.get('lead_source', '')),
                    conversion_status=str(row.get('conversion_status', '')),
                    disposition_reason=str(row.get('disposition_reason', '')),
                    x_model_used=str(row.get('x_model_used', '')),
                    variable_name=str(row.get('variable_name', ''))
                )
                
                # Try to match with existing call logs and leads
                matched = False
                
                # Enhanced phone number matching (same as simple_phone_fix.py)
                if phone_variants:
                    from .models import Lead
                    
                    # Build lead lookup dictionary for faster matching
                    if not hasattr(process_call_report_upload, '_lead_lookup'):
                        print("Building lead lookup...")
                        all_leads = Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='')
                        lead_lookup = {}
                        
                        for lead in all_leads:
                            # Extract digits from lead phone
                            lead_digits = ''.join(filter(str.isdigit, str(lead.phone_number)))
                            if len(lead_digits) >= 10:
                                # Store by last 10 digits
                                key = lead_digits[-10:]
                                if key not in lead_lookup:
                                    lead_lookup[key] = []
                                lead_lookup[key].append(lead)
                        
                        process_call_report_upload._lead_lookup = lead_lookup
                        print(f"Built lookup for {len(all_leads)} leads")
                    
                    lead_lookup = process_call_report_upload._lead_lookup
                    
                    # Try to match using the lookup
                    for phone_variant in phone_variants:
                        if len(phone_variant) >= 10:
                            search_key = phone_variant[-10:]
                            
                            if search_key in lead_lookup:
                                # Found match(es)
                                matched_lead = lead_lookup[search_key][0]  # Take first match
                                record.matched_lead = matched_lead
                                record.is_matched = True
                                matched = True
                                print(f"✅ {phone} → {matched_lead.phone_number} ({matched_lead.full_name})")
                                break
                    
                    # If still no match, try float conversion (like your script)
                    if not matched:
                        try:
                            phone_float = float(phone)
                            phone_str = str(int(phone_float))
                            if len(phone_str) >= 10:
                                search_key = phone_str[-10:]
                                if search_key in lead_lookup:
                                    matched_lead = lead_lookup[search_key][0]
                                    record.matched_lead = matched_lead
                                    record.is_matched = True
                                    matched = True
                                    print(f"✅ {phone} → {matched_lead.phone_number} ({matched_lead.full_name})")
                        except (ValueError, TypeError):
                            pass
                
                record.save()
                
                if matched:
                    matched_count += 1
                else:
                    unmatched_count += 1
                    
            except Exception as e:
                print(f"Error processing row: {e}")
                unmatched_count += 1
                continue
        
        # Update upload statistics
        upload.matched_records = matched_count
        upload.unmatched_records = unmatched_count
        upload.save()
        
        # Clear the lookup cache
        if hasattr(process_call_report_upload, '_lead_lookup'):
            delattr(process_call_report_upload, '_lead_lookup')
        
        match_rate = (matched_count / len(df) * 100) if len(df) > 0 else 0
        
        return JsonResponse({
            'success': True,
            'message': f'Processed {len(df)} records. Matched: {matched_count} ({match_rate:.1f}%), Unmatched: {unmatched_count}',
            'upload_id': upload.id,
            'total_records': len(df),
            'matched_records': matched_count,
            'unmatched_records': unmatched_count,
            'match_rate': round(match_rate, 1)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing file: {str(e)}'
        })

def call_report_dashboard(request, upload_id=None):
    """Dashboard showing call report analysis"""
    
    if upload_id:
        upload = get_object_or_404(CallReportUpload, id=upload_id)
        records = upload.records.all()
    else:
        upload = CallReportUpload.objects.first()
        records = CallReportRecord.objects.all()[:100] if not upload else upload.records.all()
    
    # Separate by lead source
    meta_records = records.filter(lead_source='Meta')
    google_records = records.filter(lead_source='Google Sheets')
    
    # Statistics
    meta_stats = {
        'total': meta_records.count(),
        'matched': meta_records.filter(is_matched=True).count(),
        'converted': meta_records.filter(conversion_status='TRUE').count(),
        'avg_duration': meta_records.aggregate(avg_duration=models.Avg('call_duration'))['avg_duration'] or 0,
        'total_cost': meta_records.aggregate(total_cost=models.Sum('cost'))['total_cost'] or 0
    }
    
    google_stats = {
        'total': google_records.count(),
        'matched': google_records.filter(is_matched=True).count(),
        'converted': google_records.filter(conversion_status='TRUE').count(),
        'avg_duration': google_records.aggregate(avg_duration=models.Avg('call_duration'))['avg_duration'] or 0,
        'total_cost': google_records.aggregate(total_cost=models.Sum('cost'))['total_cost'] or 0
    }
    
    # Recent records by source
    recent_meta = meta_records.order_by('-call_time')[:10]
    recent_google = google_records.order_by('-call_time')[:10]
    
    # Disposition breakdown
    meta_dispositions = meta_records.values('disposition').annotate(count=models.Count('id')).order_by('-count')[:5]
    google_dispositions = google_records.values('disposition').annotate(count=models.Count('id')).order_by('-count')[:5]
    
    context = {
        'upload': upload,
        'records': records,
        'meta_stats': meta_stats,
        'google_stats': google_stats,
        'recent_meta': recent_meta,
        'recent_google': recent_google,
        'meta_dispositions': meta_dispositions,
        'google_dispositions': google_dispositions,
        'recent_uploads': CallReportUpload.objects.all()[:5]
    }
    
    return render(request, 'leads/call_report_dashboard.html', context)

def call_report_api(request, upload_id=None):
    """API endpoint for call report data"""
    
    if upload_id:
        upload = get_object_or_404(CallReportUpload, id=upload_id)
        records = upload.records.all()
    else:
        records = CallReportRecord.objects.all()[:100]
    
    source_filter = request.GET.get('source', 'all')
    
    if source_filter == 'meta':
        records = records.filter(lead_source='Meta')
    elif source_filter == 'google':
        records = records.filter(lead_source='Google Sheets')
    
    data = []
    for record in records:
        data.append({
            'phone_number': record.phone_number,
            'disposition': record.disposition,
            'call_duration': record.call_duration,
            'conversion_status': record.conversion_status,
            'lead_source': record.lead_source,
            'is_matched': record.is_matched,
            'lead_name': record.matched_lead.full_name if record.matched_lead else 'Unknown',
            'call_time': record.call_time.isoformat() if record.call_time else None,
            'cost': record.cost
        })
    
    return JsonResponse({
        'records': data,
        'total_count': len(data)
    })

@csrf_exempt
def reprocess_call_report_matching(request):
    """Re-process call report matching with improved logic"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'})
    
    try:
        from .models import Lead
        
        # Get unmatched records
        unmatched_records = CallReportRecord.objects.filter(is_matched=False)
        total_unmatched = unmatched_records.count()
        
        if total_unmatched == 0:
            return JsonResponse({
                'success': True,
                'message': 'All records are already matched!',
                'newly_matched': 0,
                'total_matched': CallReportRecord.objects.filter(is_matched=True).count()
            })
        
        newly_matched = 0
        
        for record in unmatched_records:
            phone = str(record.phone_number).strip()
            if not phone or phone == 'nan':
                continue
            
            # Normalize phone number
            phone_clean = phone.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            if len(phone_clean) >= 10:
                last_10 = phone_clean[-10:]
                
                # Try multiple matching strategies
                lead = None
                
                # Use same enhanced matching as upload process
                if not hasattr(reprocess_call_report_matching, '_lead_lookup'):
                    print("Building lead lookup for reprocessing...")
                    all_leads = Lead.objects.filter(phone_number__isnull=False).exclude(phone_number='')
                    lead_lookup = {}
                    
                    for lead_obj in all_leads:
                        lead_digits = ''.join(filter(str.isdigit, str(lead_obj.phone_number)))
                        if len(lead_digits) >= 10:
                            key = lead_digits[-10:]
                            if key not in lead_lookup:
                                lead_lookup[key] = []
                            lead_lookup[key].append(lead_obj)
                    
                    reprocess_call_report_matching._lead_lookup = lead_lookup
                    print(f"Built lookup for {len(all_leads)} leads")
                
                lead_lookup = reprocess_call_report_matching._lead_lookup
                
                # Try lookup match
                if last_10 in lead_lookup:
                    lead = lead_lookup[last_10][0]
                else:
                    # Try float conversion
                    try:
                        phone_float = float(phone)
                        phone_str = str(int(phone_float))
                        if len(phone_str) >= 10:
                            search_key = phone_str[-10:]
                            if search_key in lead_lookup:
                                lead = lead_lookup[search_key][0]
                    except (ValueError, TypeError):
                        lead = None
                
                if lead:
                    record.matched_lead = lead
                    record.is_matched = True
                    record.save()
                    newly_matched += 1
        
        total_matched = CallReportRecord.objects.filter(is_matched=True).count()
        total_records = CallReportRecord.objects.count()
        match_rate = (total_matched / total_records * 100) if total_records > 0 else 0
        
        # Clear the lookup cache for next run
        if hasattr(reprocess_call_report_matching, '_lead_lookup'):
            delattr(reprocess_call_report_matching, '_lead_lookup')
        
        return JsonResponse({
            'success': True,
            'message': f'Re-processed {total_unmatched} unmatched records. Newly matched: {newly_matched}',
            'newly_matched': newly_matched,
            'total_matched': total_matched,
            'total_records': total_records,
            'match_rate': round(match_rate, 1)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error re-processing: {str(e)}'
        })