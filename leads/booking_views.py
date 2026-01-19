from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from .booking_models import UnitedNetworkBooking
from .booking_source_models import BookingSourceCategory, BookingSource

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def united_network_webhook(request):
    """Receive booking data from United Network CRM"""
    try:
        payload = json.loads(request.body)
        api_key = payload.get('api_key', '')
        
        if not api_key or not api_key.startswith('UNC-'):
            return JsonResponse({'error': 'Invalid API key'}, status=401)
        
        # Handle bulk bookings
        if payload.get('type') == 'existing_bookings_sync' or 'bookings' in payload:
            return handle_bulk_bookings(payload)
        
        # Handle single booking
        booking_data = {
            'api_key': api_key,
            'booking_id': payload.get('booking_id', ''),
            'customer_name': payload.get('customer_name', ''),
            'customer_phone': payload.get('customer_phone', ''),
            'customer_email': payload.get('customer_email', ''),
            'customer_address': payload.get('customer_address', ''),
            'nominee_name': payload.get('nominee_name', ''),
            'unit_type': payload.get('unit_type', ''),
            'unit_number': payload.get('unit_number', ''),
            'area': payload.get('area', ''),
            'total_amount': float(payload.get('total_amount', 0)),
            'booking_amount': float(payload.get('booking_amount', 0)),
            'project_name': payload.get('project_name', ''),
            'project_location': payload.get('project_location', ''),
            'developer': payload.get('developer', ''),
            'cp_code': payload.get('cp_code', ''),
            'cp_company': payload.get('cp_company', ''),
            'cp_name': payload.get('cp_name', ''),
            'cp_phone': payload.get('cp_phone', ''),
            'cp_email': payload.get('cp_email', ''),
            'status': payload.get('status', 'received'),
            'booking_source': payload.get('booking_source', 'web_form'),
            'created_at': datetime.fromisoformat(payload.get('created_at', timezone.now().isoformat()).replace('Z', '+00:00')),
            'raw_payload': payload
        }
        
        booking, created = UnitedNetworkBooking.objects.update_or_create(
            booking_id=booking_data['booking_id'],
            defaults=booking_data
        )
        
        logger.info(f"{'Created' if created else 'Updated'} booking: {booking.booking_id}")
        
        return JsonResponse({
            'success': True,
            'booking_id': booking.booking_id,
            'status': 'created' if created else 'updated'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def handle_bulk_bookings(payload):
    """Handle bulk booking data from United Network CRM"""
    try:
        bookings_data = payload.get('bookings', [])
        created_count = 0
        updated_count = 0
        
        for booking_payload in bookings_data:
            booking_data = {
                'api_key': payload.get('api_key'),
                'booking_id': booking_payload.get('booking_id', ''),
                'customer_name': booking_payload.get('customer_name', ''),
                'customer_phone': booking_payload.get('customer_phone', ''),
                'customer_email': booking_payload.get('customer_email', ''),
                'customer_address': booking_payload.get('customer_address', ''),
                'nominee_name': booking_payload.get('nominee_name', ''),
                'unit_type': booking_payload.get('unit_type', ''),
                'unit_number': booking_payload.get('unit_number', ''),
                'area': booking_payload.get('area', ''),
                'total_amount': float(booking_payload.get('total_amount', 0)),
                'booking_amount': float(booking_payload.get('booking_amount', 0)),
                'project_name': booking_payload.get('project_name', ''),
                'project_location': booking_payload.get('project_location', ''),
                'developer': booking_payload.get('developer', ''),
                'cp_code': booking_payload.get('cp_code', ''),
                'cp_company': booking_payload.get('cp_company', ''),
                'cp_name': booking_payload.get('cp_name', ''),
                'cp_phone': booking_payload.get('cp_phone', ''),
                'cp_email': booking_payload.get('cp_email', ''),
                'status': booking_payload.get('status', 'received'),
                'booking_source': booking_payload.get('booking_source', 'web_form'),
                'created_at': datetime.fromisoformat(booking_payload.get('created_at', timezone.now().isoformat()).replace('Z', '+00:00')),
                'raw_payload': booking_payload
            }
            
            booking, created = UnitedNetworkBooking.objects.update_or_create(
                booking_id=booking_data['booking_id'],
                defaults=booking_data
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        logger.info(f"Bulk sync: {created_count} created, {updated_count} updated")
        
        return JsonResponse({
            'success': True,
            'total_received': len(bookings_data),
            'created': created_count,
            'updated': updated_count,
            'type': 'bulk_sync'
        })
        
    except Exception as e:
        logger.error(f"Bulk booking error: {str(e)}")
        return JsonResponse({'error': 'Bulk processing failed'}, status=500)

@staff_member_required
def bookings_dashboard(request):
    """Admin-only dashboard to view United Network bookings"""
    
    # Get filter parameters
    search = request.GET.get('search', '')
    project_filter = request.GET.get('project', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    bookings = UnitedNetworkBooking.objects.all()
    
    # Apply filters
    if search:
        bookings = bookings.filter(
            Q(customer_name__icontains=search) |
            Q(customer_phone__icontains=search) |
            Q(booking_id__icontains=search) |
            Q(project_name__icontains=search)
        )
    
    if project_filter:
        bookings = bookings.filter(project_name__icontains=project_filter)
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    if date_from:
        bookings = bookings.filter(created_at__date__gte=date_from)
    
    if date_to:
        bookings = bookings.filter(created_at__date__lte=date_to)
    
    # Calculate statistics
    total_bookings = bookings.count()
    total_value = bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Recent bookings (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_bookings = bookings.filter(created_at__gte=week_ago).count()
    
    # Project-wise breakdown
    project_stats = bookings.values('project_name').annotate(
        count=Count('id'),
        total_value=Sum('total_amount')
    ).order_by('-count')[:10]
    
    # Status breakdown
    status_stats = bookings.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Pagination
    paginator = Paginator(bookings.order_by('-received_at'), 25)
    page = request.GET.get('page')
    bookings_page = paginator.get_page(page)
    
    # Get unique values for filters
    projects = UnitedNetworkBooking.objects.values_list('project_name', flat=True).distinct()
    statuses = UnitedNetworkBooking.objects.values_list('status', flat=True).distinct()
    
    context = {
        'bookings': bookings_page,
        'total_bookings': total_bookings,
        'total_value': total_value,
        'recent_bookings': recent_bookings,
        'project_stats': project_stats,
        'status_stats': status_stats,
        'projects': projects,
        'statuses': statuses,
        'search': search,
        'project_filter': project_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'leads/bookings_dashboard.html', context)

@staff_member_required
def booking_detail(request, booking_id):
    """View detailed information about a specific booking"""
    try:
        booking = UnitedNetworkBooking.objects.get(id=booking_id)
        
        # Handle source update
        if request.method == 'POST':
            source_category_id = request.POST.get('source_category')
            source_detail_id = request.POST.get('source_detail')
            custom_source = request.POST.get('custom_source', '').strip()
            
            if source_category_id:
                booking.source_category_id = source_category_id
            if source_detail_id:
                booking.source_detail_id = source_detail_id
            if custom_source:
                booking.custom_source = custom_source
            
            booking.save()
            return JsonResponse({'success': True, 'message': 'Source updated successfully'})
        
        # Get source data for dropdowns
        source_categories = BookingSourceCategory.objects.filter(is_active=True)
        
        context = {
            'booking': booking,
            'source_categories': source_categories
        }
        
        return render(request, 'leads/booking_detail.html', context)
    except UnitedNetworkBooking.DoesNotExist:
        return render(request, 'leads/booking_not_found.html', status=404)

@staff_member_required
def bookings_api(request):
    """API endpoint for booking statistics"""
    
    # Get date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    bookings = UnitedNetworkBooking.objects.filter(created_at__gte=start_date)
    
    # Daily breakdown
    daily_data = []
    for i in range(days):
        date = start_date.date() + timedelta(days=i)
        day_bookings = bookings.filter(created_at__date=date)
        daily_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': day_bookings.count(),
            'value': float(day_bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
        })
    
    return JsonResponse({
        'daily_data': daily_data,
        'total_bookings': bookings.count(),
        'total_value': float(bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
    })