#!/usr/bin/env python3
"""
Add Auto Call Dashboard View
"""

# Add this to bulk_call_upload_views.py at the end:

def auto_call_dashboard(request):
    """Dashboard for auto-calling new leads"""
    return render(request, 'leads/auto_call_dashboard.html')