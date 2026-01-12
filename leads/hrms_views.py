from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import TeamMember, Lead, LeadAssignment
from .hrms_models import (
    EmployeeProfile, Attendance, LeaveRequest, LeaveBalance, 
    Payroll, PerformanceReview, Goal
)
import json

def enhanced_profile_view(request):
    """Enhanced profile view with HRMS functionality"""
    if not request.session.get('is_team_member'):
        return redirect('team_login')
    
    team_member_id = request.session.get('team_member_id')
    team_member = get_object_or_404(TeamMember, id=team_member_id)
    
    # Get or create HRMS profile
    hrms_profile, created = EmployeeProfile.objects.get_or_create(
        team_member=team_member,
        defaults={
            'employee_id': f"EMP{team_member.id:04d}",
            'joining_date': team_member.created_at.date(),
            'department': 'Sales',
        }
    )
    
    # Get or create leave balance for current year
    current_year = timezone.now().year
    leave_balance, created = LeaveBalance.objects.get_or_create(
        team_member=team_member,
        year=current_year
    )
    
    # Performance stats
    total_assigned = Lead.objects.filter(assignment__assigned_to=team_member).count()
    completed = Lead.objects.filter(
        assignment__assigned_to=team_member,
        assignment__is_attended=True
    ).count()
    pending = Lead.objects.filter(
        assignment__assigned_to=team_member,
        assignment__is_attended=False
    ).count()
    conversion_rate = (completed / total_assigned * 100) if total_assigned > 0 else 0
    
    # Get subordinates
    subordinates = TeamMember.objects.filter(parent_user=team_member, is_active=True)
    
    # Add assigned leads count to subordinates
    for subordinate in subordinates:
        subordinate.assigned_leads_count = Lead.objects.filter(
            assignment__assigned_to=subordinate
        ).count()
    
    context = {
        'team_member': team_member,
        'hrms_data': hrms_profile,
        'leave_balance': leave_balance,
        'subordinates': subordinates,
        'stats': {
            'total_assigned': total_assigned,
            'completed': completed,
            'pending': pending,
            'conversion_rate': round(conversion_rate, 1)
        }
    }
    
    return render(request, 'leads/enhanced_profile.html', context)

@csrf_exempt
def update_personal_info(request):
    """Update personal information"""
    if not request.session.get('is_team_member'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        team_member_id = request.session.get('team_member_id')
        team_member = get_object_or_404(TeamMember, id=team_member_id)
        
        # Get or create HRMS profile
        hrms_profile, created = EmployeeProfile.objects.get_or_create(
            team_member=team_member
        )
        
        # Update fields
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth:
            hrms_profile.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        
        hrms_profile.gender = request.POST.get('gender', '')
        hrms_profile.blood_group = request.POST.get('blood_group', '')
        hrms_profile.emergency_contact = request.POST.get('emergency_contact', '')
        hrms_profile.address = request.POST.get('address', '')
        hrms_profile.pan_number = request.POST.get('pan_number', '')
        
        hrms_profile.save()
        
        messages.success(request, 'Personal information updated successfully!')
        return redirect('enhanced_profile')
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def apply_leave(request):
    """Apply for leave"""
    if not request.session.get('is_team_member'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        team_member_id = request.session.get('team_member_id')
        team_member = get_object_or_404(TeamMember, id=team_member_id)
        
        leave_type = request.POST.get('leave_type')
        from_date = datetime.strptime(request.POST.get('from_date'), '%Y-%m-%d').date()
        to_date = datetime.strptime(request.POST.get('to_date'), '%Y-%m-%d').date()
        reason = request.POST.get('reason')
        
        # Calculate days
        days_requested = (to_date - from_date).days + 1
        
        # Check leave balance
        current_year = timezone.now().year
        leave_balance, created = LeaveBalance.objects.get_or_create(
            team_member=team_member,
            year=current_year
        )
        
        # Check if sufficient balance
        balance_field = f"{leave_type}_leave"
        current_balance = getattr(leave_balance, balance_field, 0)
        
        if days_requested > current_balance:
            messages.error(request, f'Insufficient {leave_type} leave balance. Available: {current_balance} days')
            return redirect('enhanced_profile')
        
        # Create leave request
        leave_request = LeaveRequest.objects.create(
            team_member=team_member,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date,
            days_requested=days_requested,
            reason=reason
        )
        
        messages.success(request, 'Leave application submitted successfully!')
        return redirect('enhanced_profile')
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def attendance_summary(request):
    """Get attendance summary for current month"""
    if not request.session.get('is_team_member'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    team_member_id = request.session.get('team_member_id')
    team_member = get_object_or_404(TeamMember, id=team_member_id)
    
    # Get current month attendance
    now = timezone.now()
    start_of_month = now.replace(day=1)
    
    attendance_records = Attendance.objects.filter(
        team_member=team_member,
        date__gte=start_of_month.date(),
        date__lte=now.date()
    )
    
    # Calculate stats
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = attendance_records.filter(status='absent').count()
    late_days = attendance_records.filter(status='late').count()
    
    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
    
    return JsonResponse({
        'success': True,
        'data': {
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'attendance_rate': round(attendance_rate, 1)
        }
    })

def payroll_summary(request):
    """Get payroll summary"""
    if not request.session.get('is_team_member'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    team_member_id = request.session.get('team_member_id')
    team_member = get_object_or_404(TeamMember, id=team_member_id)
    
    # Get latest payroll record
    latest_payroll = Payroll.objects.filter(team_member=team_member).first()
    
    if not latest_payroll:
        # Create default payroll for demo
        now = timezone.now()
        latest_payroll = Payroll.objects.create(
            team_member=team_member,
            month=now.month,
            year=now.year,
            basic_salary=45000,
            hra=8000,
            transport_allowance=2000,
            medical_allowance=1500,
            pf_deduction=5400,
            tax_deduction=3200,
            other_deductions=500
        )
    
    return JsonResponse({
        'success': True,
        'data': {
            'basic_salary': float(latest_payroll.basic_salary),
            'gross_salary': float(latest_payroll.gross_salary),
            'net_salary': float(latest_payroll.net_salary),
            'total_allowances': float(
                latest_payroll.hra + latest_payroll.transport_allowance + 
                latest_payroll.medical_allowance + latest_payroll.other_allowances
            ),
            'total_deductions': float(
                latest_payroll.pf_deduction + latest_payroll.tax_deduction + 
                latest_payroll.other_deductions
            )
        }
    })

def performance_summary(request):
    """Get performance summary"""
    if not request.session.get('is_team_member'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    team_member_id = request.session.get('team_member_id')
    team_member = get_object_or_404(TeamMember, id=team_member_id)
    
    # Get current month goals
    now = timezone.now()
    current_goals = Goal.objects.filter(
        team_member=team_member,
        start_date__lte=now.date(),
        end_date__gte=now.date()
    )
    
    # Calculate performance metrics
    total_assigned = Lead.objects.filter(assignment__assigned_to=team_member).count()
    completed = Lead.objects.filter(
        assignment__assigned_to=team_member,
        assignment__is_attended=True
    ).count()
    
    # Get latest performance review
    latest_review = PerformanceReview.objects.filter(team_member=team_member).first()
    
    goals_data = []
    for goal in current_goals:
        goals_data.append({
            'title': goal.title,
            'target': float(goal.target_value),
            'current': float(goal.current_value),
            'progress': goal.progress_percentage,
            'status': goal.status
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'leads_assigned': total_assigned,
            'leads_converted': completed,
            'conversion_rate': (completed / total_assigned * 100) if total_assigned > 0 else 0,
            'performance_rating': latest_review.overall_rating if latest_review else 4.2,
            'goals': goals_data
        }
    })

def leave_history(request):
    """Get leave history"""
    if not request.session.get('is_team_member'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    team_member_id = request.session.get('team_member_id')
    team_member = get_object_or_404(TeamMember, id=team_member_id)
    
    leave_requests = LeaveRequest.objects.filter(team_member=team_member)[:10]
    
    leaves_data = []
    for leave in leave_requests:
        leaves_data.append({
            'leave_type': leave.get_leave_type_display(),
            'from_date': leave.from_date.strftime('%b %d, %Y'),
            'to_date': leave.to_date.strftime('%b %d, %Y'),
            'days': leave.days_requested,
            'status': leave.status,
            'reason': leave.reason,
            'applied_on': leave.created_at.strftime('%b %d, %Y')
        })
    
    return JsonResponse({
        'success': True,
        'data': leaves_data
    })

@csrf_exempt
def mark_attendance(request):
    """Mark attendance for today"""
    if not request.session.get('is_team_member'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        team_member_id = request.session.get('team_member_id')
        team_member = get_object_or_404(TeamMember, id=team_member_id)
        
        today = timezone.now().date()
        
        # Check if already marked
        existing_attendance = Attendance.objects.filter(
            team_member=team_member,
            date=today
        ).first()
        
        if existing_attendance:
            return JsonResponse({
                'success': False, 
                'error': 'Attendance already marked for today'
            })
        
        # Mark attendance
        current_time = timezone.now().time()
        status = 'present'
        
        # Check if late (after 10 AM)
        if current_time.hour >= 10:
            status = 'late'
        
        attendance = Attendance.objects.create(
            team_member=team_member,
            date=today,
            status=status,
            check_in_time=current_time
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Attendance marked as {status}',
            'check_in_time': current_time.strftime('%H:%M')
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})