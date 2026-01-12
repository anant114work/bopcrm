from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .booking_source_models import BookingSourceCategory, BookingSource
import json

def get_source_categories(request):
    """Get all active source categories"""
    categories = BookingSourceCategory.objects.filter(is_active=True)
    return JsonResponse({
        'categories': [{'id': cat.id, 'name': cat.name} for cat in categories]
    })

def get_sources_by_category(request, category_id):
    """Get sources for a specific category"""
    try:
        sources = BookingSource.objects.filter(category_id=category_id, is_active=True)
        return JsonResponse({
            'sources': [{'id': src.id, 'name': src.name} for src in sources]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def create_custom_source(request):
    """Create a new custom source"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_id = data.get('category_id')
            source_name = data.get('source_name')
            
            if not category_id or not source_name:
                return JsonResponse({'error': 'Category ID and source name required'}, status=400)
            
            category = BookingSourceCategory.objects.get(id=category_id)
            source, created = BookingSource.objects.get_or_create(
                category=category,
                name=source_name,
                defaults={'is_active': True}
            )
            
            return JsonResponse({
                'success': True,
                'source': {'id': source.id, 'name': source.name},
                'created': created
            })
            
        except BookingSourceCategory.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'POST method required'}, status=405)