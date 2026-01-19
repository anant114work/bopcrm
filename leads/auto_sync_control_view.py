from django.shortcuts import render

def auto_sync_control(request):
    """Auto sync control page"""
    return render(request, 'leads/auto_sync_control.html')