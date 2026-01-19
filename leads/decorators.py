from django.shortcuts import redirect
from functools import wraps

def login_required(view_func):
    """Require login for all views"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_team_member'):
            return redirect('team_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """Require admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_team_member'):
            return redirect('team_login')
        if not request.session.get('is_admin'):
            return redirect('my_leads')
        return view_func(request, *args, **kwargs)
    return wrapper
