from django.shortcuts import render

def auto_call_dashboard(request):
    """Dashboard for auto-calling new leads"""
    return render(request, 'leads/auto_call_dashboard.html')