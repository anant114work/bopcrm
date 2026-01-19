#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.core.management.commands.runserver import Command as RunServerCommand

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
    
    # Run with SSL
    sys.argv = ['manage.py', 'runserver', '127.0.0.1:8002', '--cert-file', 'cert.crt', '--key-file', 'cert.key']
    
    try:
        execute_from_command_line(sys.argv)
    except:
        # Fallback to regular HTTP
        print("HTTPS failed, running HTTP server...")
        sys.argv = ['manage.py', 'runserver', '127.0.0.1:8002']
        execute_from_command_line(sys.argv)