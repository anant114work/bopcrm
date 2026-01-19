from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TeamMember
from .decorators import admin_required
import json

@admin_required
def user_management(request):
    """User management page - Admin only"""
    users = TeamMember.objects.all().order_by('-created_at')
    
    context = {
        'users': users,
        'role_choices': TeamMember.ROLE_CHOICES
    }
    return render(request, 'leads/user_management.html', context)

@admin_required
@csrf_exempt
def create_user(request):
    """Create new user - Admin only"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            role = data.get('role', 'Sales Executive - T5')
            parent_id = data.get('parent_id')
            
            if not name or not phone:
                return JsonResponse({'success': False, 'error': 'Name and phone are required'})
            
            # Check if phone already exists
            if TeamMember.objects.filter(phone=phone).exists():
                return JsonResponse({'success': False, 'error': 'Phone number already exists'})
            
            # Check if email already exists (if provided)
            if email and TeamMember.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'Email already exists'})
            
            # Get parent user if specified
            parent_user = None
            if parent_id:
                try:
                    parent_user = TeamMember.objects.get(id=parent_id)
                except TeamMember.DoesNotExist:
                    pass
            
            # Create user
            user = TeamMember.objects.create(
                name=name,
                email=email or f"{phone}@temp.com",
                phone=phone,
                role=role,
                parent_user=parent_user,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': f'User {name} created successfully',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone,
                    'role': user.role
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@admin_required
@csrf_exempt
def toggle_user(request):
    """Toggle user active status - Admin only"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            user = TeamMember.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            
            return JsonResponse({
                'success': True,
                'is_active': user.is_active,
                'message': f'User {user.name} {"activated" if user.is_active else "deactivated"}'
            })
            
        except TeamMember.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@admin_required
@csrf_exempt
def delete_user(request):
    """Delete user - Admin only"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            user = TeamMember.objects.get(id=user_id)
            
            # Don't allow deleting admin
            if user.role == 'Admin':
                return JsonResponse({'success': False, 'error': 'Cannot delete admin user'})
            
            user_name = user.name
            user.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'User {user_name} deleted successfully'
            })
            
        except TeamMember.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@admin_required
@csrf_exempt
def update_user(request):
    """Update user details - Admin only"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            user = TeamMember.objects.get(id=user_id)
            
            # Update fields if provided
            if 'name' in data:
                user.name = data['name'].strip()
            if 'email' in data:
                email = data['email'].strip()
                if email and TeamMember.objects.filter(email=email).exclude(id=user_id).exists():
                    return JsonResponse({'success': False, 'error': 'Email already exists'})
                user.email = email or f"{user.phone}@temp.com"
            if 'phone' in data:
                phone = data['phone'].strip()
                if TeamMember.objects.filter(phone=phone).exclude(id=user_id).exists():
                    return JsonResponse({'success': False, 'error': 'Phone already exists'})
                user.phone = phone
            if 'role' in data:
                user.role = data['role']
            if 'parent_id' in data:
                parent_id = data['parent_id']
                if parent_id:
                    try:
                        user.parent_user = TeamMember.objects.get(id=parent_id)
                    except TeamMember.DoesNotExist:
                        pass
                else:
                    user.parent_user = None
            
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': f'User {user.name} updated successfully',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone,
                    'role': user.role
                }
            })
            
        except TeamMember.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
