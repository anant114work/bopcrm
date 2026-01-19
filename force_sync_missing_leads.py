#!/usr/bin/env python
"""
Force sync missing Google Sheets leads
"""

import os
import sys
import django
from datetime import datetime, date

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

def force_sync_dec15_leads():
    """Force sync Dec 15 leads that are missing"""
    
    # Dec 15 leads from your data
    dec15_leads = [
        {
            'name': 'Suman Kumar',
            'phone': '8540863684',
            'email': 'aabusuman969@gmail.com',
            'time': '08:01:36'
        },
        {
            'name': 'Suman Kumar',
            'phone': '8540863684', 
            'email': 'aabusuman969@gmail.com',
            'time': '08:02:20'
        },
        {
            'name': 'Sunil Mehra',
            'phone': '9814109060',
            'email': 'sunilmehra_asr@yahoo.co.in',
            'time': '08:27:38'
        }
    ]
    
    created_count = 0
    
    for lead_data in dec15_leads:
        # Check if lead already exists
        existing = Lead.objects.filter(
            phone_number__contains=lead_data['phone'][-10:]
        ).first()
        
        if not existing:
            # Create new lead
            lead = Lead.objects.create(
                lead_id=f"GOOGLE_DEC15_{lead_data['phone']}_{lead_data['time'].replace(':', '')}",
                full_name=lead_data['name'],
                phone_number=f"+91{lead_data['phone']}",
                email=lead_data['email'],
                source='Google Sheets',
                form_name='Google Sheets - AU Aspire Leisure Valley',
                created_time=datetime(2025, 12, 15, int(lead_data['time'][:2]), int(lead_data['time'][3:5]), int(lead_data['time'][6:8]))
            )
            created_count += 1
            print(f"✅ Created: {lead_data['name']} ({lead_data['phone']})")
        else:
            print(f"⚠️ Already exists: {lead_data['name']} ({lead_data['phone']})")
    
    print(f"\n🎉 Created {created_count} missing Dec 15 leads!")

def check_recent_leads():
    """Check what leads we have for recent dates"""
    print("📊 Recent leads in database:")
    
    recent_leads = Lead.objects.filter(
        created_time__date__gte=date(2025, 12, 13)
    ).order_by('-created_time')[:20]
    
    for lead in recent_leads:
        print(f"   {lead.created_time.strftime('%m/%d %H:%M')} - {lead.full_name} ({lead.phone_number}) - {lead.source}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 FORCE SYNC MISSING GOOGLE LEADS")
    print("=" * 60)
    
    check_recent_leads()
    print("\n" + "-" * 60)
    force_sync_dec15_leads()
    
    print("\n" + "=" * 60)