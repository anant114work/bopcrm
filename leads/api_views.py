from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .booking_models import UnitedNetworkBooking
import json

def validate_api_key(request):
    """Validate API key from header or query parameter"""
    api_key = request.headers.get('X-API-Key') or request.GET.get('api_key')
    return api_key and api_key.startswith('UNC-')

@csrf_exempt
def api_status(request):
    """API status endpoint"""
    if not validate_api_key(request):
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    total_bookings = UnitedNetworkBooking.objects.count()
    return JsonResponse({
        'status': 'active',
        'total_bookings': total_bookings,
        'endpoints': {
            'get_all_bookings': '/api/external/bookings/',
            'get_booking_details': '/api/external/booking/{booking_id}/',
            'search_bookings': '/api/external/search/',
            'api_status': '/api/external/status/'
        }
    })

@csrf_exempt
def api_bookings_list(request):
    """Get all bookings with pagination"""
    if not validate_api_key(request):
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = min(int(request.GET.get('per_page', 20)), 100)  # Max 100 per page
    
    bookings = UnitedNetworkBooking.objects.all().order_by('-received_at')
    paginator = Paginator(bookings, per_page)
    page_obj = paginator.get_page(page)
    
    # Format booking data
    bookings_data = []
    for booking in page_obj:
        bookings_data.append({
            'booking_id': booking.booking_id,
            'customer_name': booking.customer_name,
            'customer_phone': booking.customer_phone,
            'customer_email': booking.customer_email,
            'project_name': booking.project_name,
            'project_location': booking.project_location,
            'unit_type': booking.unit_type,
            'unit_number': booking.unit_number,
            'area': booking.area,
            'total_amount': str(booking.total_amount),
            'booking_amount': str(booking.booking_amount),
            'status': booking.status,
            'cp_code': booking.cp_code,
            'cp_company': booking.cp_company,
            'cp_name': booking.cp_name,
            'created_at': booking.created_at.isoformat(),
            'received_at': booking.received_at.isoformat()
        })
    
    return JsonResponse({
        'success': True,
        'bookings': bookings_data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_bookings': paginator.count,
            'per_page': per_page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    })

@csrf_exempt
def api_booking_detail(request, booking_id):
    """Get specific booking details"""
    if not validate_api_key(request):
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    try:
        booking = UnitedNetworkBooking.objects.get(booking_id=booking_id)
        
        booking_data = {
            'booking_id': booking.booking_id,
            'api_key': booking.api_key,
            'customer_name': booking.customer_name,
            'customer_phone': booking.customer_phone,
            'customer_email': booking.customer_email,
            'customer_address': booking.customer_address,
            'nominee_name': booking.nominee_name,
            'unit_type': booking.unit_type,
            'unit_number': booking.unit_number,
            'area': booking.area,
            'total_amount': str(booking.total_amount),
            'booking_amount': str(booking.booking_amount),
            'project_name': booking.project_name,
            'project_location': booking.project_location,
            'developer': booking.developer,
            'cp_code': booking.cp_code,
            'cp_company': booking.cp_company,
            'cp_name': booking.cp_name,
            'cp_phone': booking.cp_phone,
            'cp_email': booking.cp_email,
            'status': booking.status,
            'booking_source': booking.booking_source,
            'created_at': booking.created_at.isoformat(),
            'received_at': booking.received_at.isoformat(),
            'formatted_amount': booking.formatted_amount
        }
        
        return JsonResponse({
            'success': True,
            'booking': booking_data
        })
        
    except UnitedNetworkBooking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)

@csrf_exempt
def api_search_bookings(request):
    """Search bookings with filters"""
    if not validate_api_key(request):
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    bookings = UnitedNetworkBooking.objects.all()
    
    # Apply filters
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status__icontains=status)
    
    cp_code = request.GET.get('cp_code')
    if cp_code:
        bookings = bookings.filter(cp_code__icontains=cp_code)
    
    project = request.GET.get('project')
    if project:
        bookings = bookings.filter(project_name__icontains=project)
    
    customer = request.GET.get('customer')
    if customer:
        bookings = bookings.filter(
            Q(customer_name__icontains=customer) |
            Q(customer_phone__icontains=customer)
        )
    
    date_from = request.GET.get('date_from')
    if date_from:
        bookings = bookings.filter(created_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        bookings = bookings.filter(created_at__date__lte=date_to)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = min(int(request.GET.get('per_page', 20)), 100)
    
    bookings = bookings.order_by('-received_at')
    paginator = Paginator(bookings, per_page)
    page_obj = paginator.get_page(page)
    
    # Format results
    results = []
    for booking in page_obj:
        results.append({
            'booking_id': booking.booking_id,
            'customer_name': booking.customer_name,
            'customer_phone': booking.customer_phone,
            'project_name': booking.project_name,
            'unit_number': booking.unit_number,
            'total_amount': str(booking.total_amount),
            'status': booking.status,
            'cp_code': booking.cp_code,
            'cp_company': booking.cp_company,
            'created_at': booking.created_at.isoformat()
        })
    
    return JsonResponse({
        'success': True,
        'results': results,
        'total_found': paginator.count,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'per_page': per_page
        },
        'filters_applied': {
            'status': status,
            'cp_code': cp_code,
            'project': project,
            'customer': customer,
            'date_from': date_from,
            'date_to': date_to
        }
    })