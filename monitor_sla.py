#!/usr/bin/env python
"""
SLA Monitoring Script
Run this every 5 minutes via cron job to reassign overdue leads
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.assignment import RoundRobinAssigner

def main():
    assigner = RoundRobinAssigner()
    reassigned_count = assigner.reassign_overdue_leads()
    
    if reassigned_count > 0:
        print(f"Reassigned {reassigned_count} overdue leads")
    else:
        print("No overdue leads found")

if __name__ == "__main__":
    main()