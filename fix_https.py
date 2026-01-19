#!/usr/bin/env python
"""
Simple HTTP server to bypass HTTPS issues
Run this instead of Django dev server
"""
import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from wsgiref.simple_server import make_server

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

# Get Django WSGI application
application = get_wsgi_application()

def run_server():
    print("Starting CRM server on http://127.0.0.1:8080/")
    print("Access your CRM at: http://127.0.0.1:8080/")
    print("Login credentials:")
    print("- Username: gaurav, Password: 9910266552")
    print("- Username: amit, Password: 8130040959") 
    print("- Username: ankush, Password: 9871627302")
    print("\nPress Ctrl+C to stop")
    
    try:
        server = make_server('127.0.0.1', 8080, application)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    run_server()