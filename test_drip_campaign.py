#!/usr/bin/env python
"""
Test script for Gaur Yamuna Drip Campaign System
Run this after setting up the drip campaign to test functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead
from leads.project_models import Project
from leads.drip_campaign_models import DripCampaign, DripMessage, DripSubscriber
from leads.drip_campaign_views import send_drip_message
from django.utils import timezone

def test_drip_campaign():
    print("🚀 Testing Gaur Yamuna Drip Campaign System")
    print("=" * 50)
    
    # 1. Check if Gaur Yamuna project exists
    try:
        project = Project.objects.get(name='Gaur Yamuna')
        print(f"✅ Project found: {project.name}")
    except Project.DoesNotExist:
        print("❌ Gaur Yamuna project not found. Creating...")
        project = Project.objects.create(
            name='Gaur Yamuna',
            code='gaur_yamuna',
            developer='Gaur Group',
            location='Yamuna Expressway'
        )
        print(f"✅ Created project: {project.name}")
    
    # 2. Check if drip campaign exists
    try:
        campaign = DripCampaign.objects.get(name='Gaur Yamuna Follow-up Sequence')
        print(f"✅ Campaign found: {campaign.name}")
        print(f"   Status: {campaign.status}")
        print(f"   Messages: {campaign.messages.count()}")
    except DripCampaign.DoesNotExist:
        print("❌ Drip campaign not found. Please create it first via the web interface.")
        return
    
    # 3. Show campaign messages
    print("\n📋 Campaign Messages:")
    messages = campaign.messages.all().order_by('day_number')
    for msg in messages:
        print(f"   Day {msg.day_number}: {msg.template_name}")
        print(f"   Delay: {msg.delay_hours} hours")
        print(f"   Sent: {msg.sent_count}, Failed: {msg.failed_count}")
        print()
    
    # 4. Check for test leads
    test_leads = Lead.objects.filter(
        phone_number__in=['919999999999', '918888888888', '917777777777']
    )
    
    if test_leads.exists():
        print(f"📞 Found {test_leads.count()} test leads")
        for lead in test_leads:
            print(f"   {lead.full_name} - {lead.phone_number}")
    else:
        print("📞 No test leads found. Creating a test lead...")
        test_lead = Lead.objects.create(
            lead_id='TEST_DRIP_001',
            created_time=timezone.now(),
            full_name='Test User Drip',
            phone_number='919999999999',
            email='test@example.com',
            form_name='gaur_yamuna_test'
        )
        print(f"   Created test lead: {test_lead.full_name} - {test_lead.phone_number}")
        test_leads = [test_lead]
    
    # 5. Check subscribers
    subscribers = DripSubscriber.objects.filter(campaign=campaign)
    print(f"\n👥 Current subscribers: {subscribers.count()}")
    
    for subscriber in subscribers:
        print(f"   {subscriber.first_name} ({subscriber.phone_number})")
        print(f"   Status: {subscriber.status}, Current Day: {subscriber.current_day}")
        if subscriber.next_message_at:
            print(f"   Next message: {subscriber.next_message_at}")
        print()
    
    # 6. Test subscription (optional)
    print("\n🔧 Test Options:")
    print("1. Subscribe a test lead to the campaign")
    print("2. Process pending messages")
    print("3. Show campaign analytics")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        # Subscribe first test lead
        if test_leads:
            lead = test_leads[0] if hasattr(test_leads, '__iter__') else test_leads.first()
            
            # Check if already subscribed
            existing = DripSubscriber.objects.filter(campaign=campaign, lead=lead).first()
            if existing:
                print(f"❌ {lead.full_name} is already subscribed")
            else:
                subscriber = DripSubscriber.objects.create(
                    campaign=campaign,
                    lead=lead,
                    phone_number=lead.phone_number,
                    first_name=lead.full_name or 'Test User',
                    status='active'
                )
                
                # Schedule first message
                first_message = campaign.messages.filter(day_number=1).first()
                if first_message and first_message.delay_hours == 0:
                    print(f"📤 Sending immediate welcome message...")
                    result = send_drip_message(subscriber, first_message)
                    if result['success']:
                        subscriber.current_day = 1
                        subscriber.schedule_next_message()
                        print(f"✅ Welcome message sent successfully!")
                    else:
                        print(f"❌ Failed to send message: {result['error']}")
                else:
                    subscriber.next_message_at = timezone.now()
                    subscriber.save()
                    print(f"✅ Subscribed {lead.full_name} to campaign")
    
    elif choice == '2':
        # Process pending messages
        from leads.drip_campaign_views import process_pending_messages
        print("📤 Processing pending messages...")
        # This would normally be called via the web interface
        print("Use the web interface or management command to process messages")
    
    elif choice == '3':
        # Show analytics
        total_subscribers = DripSubscriber.objects.filter(campaign=campaign).count()
        active_subscribers = DripSubscriber.objects.filter(campaign=campaign, status='active').count()
        completed_subscribers = DripSubscriber.objects.filter(campaign=campaign, status='completed').count()
        
        print(f"\n📊 Campaign Analytics:")
        print(f"   Total Subscribers: {total_subscribers}")
        print(f"   Active Subscribers: {active_subscribers}")
        print(f"   Completed Subscribers: {completed_subscribers}")
        
        total_sent = sum(msg.sent_count for msg in messages)
        total_failed = sum(msg.failed_count for msg in messages)
        
        print(f"   Total Messages Sent: {total_sent}")
        print(f"   Total Messages Failed: {total_failed}")
        
        if total_sent + total_failed > 0:
            success_rate = (total_sent / (total_sent + total_failed)) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
    
    print("\n✅ Test completed!")
    print("\n🌐 Access the drip campaigns dashboard at: http://localhost:8000/drip-campaigns/")

if __name__ == '__main__':
    test_drip_campaign()