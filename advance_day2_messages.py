#!/usr/bin/env python
"""
Script to advance all Day 1 subscribers to Day 2 messages
This will send Day 2 messages to all leads who have already received Day 1 messages
"""

import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.drip_campaign_models import DripSubscriber, DripMessage, DripMessageLog
from leads.drip_auto_sender import send_drip_message

def advance_to_day2():
    """Advance all Day 1 subscribers to Day 2"""
    print("🚀 Starting Day 2 message advancement...")
    
    # Find all subscribers who are currently on Day 1 (have received Day 1 message)
    day1_subscribers = DripSubscriber.objects.filter(
        status='active',
        current_day=1
    )
    
    print(f"📊 Found {day1_subscribers.count()} subscribers currently on Day 1")
    
    if day1_subscribers.count() == 0:
        print("❌ No Day 1 subscribers found. Nothing to advance.")
        return
    
    # Get Day 2 message for each campaign
    campaigns_processed = set()
    total_advanced = 0
    total_scheduled = 0
    
    for subscriber in day1_subscribers:
        campaign = subscriber.campaign
        
        if campaign.id not in campaigns_processed:
            print(f"\n📋 Processing campaign: {campaign.name}")
            campaigns_processed.add(campaign.id)
        
        # Get Day 2 message for this campaign
        day2_message = campaign.messages.filter(day_number=2, is_active=True).first()
        
        if not day2_message:
            print(f"⚠️ No Day 2 message found for campaign {campaign.name}")
            continue
        
        # Check if Day 2 already sent to this subscriber
        existing_day2 = DripMessageLog.objects.filter(
            phone_number=subscriber.phone_number,
            drip_message=day2_message,
            status='sent'
        ).exists()
        
        if existing_day2:
            print(f"⚠️ Day 2 already sent to {subscriber.phone_number}")
            continue
        
        print(f"📱 Advancing {subscriber.first_name} ({subscriber.phone_number}) to Day 2")
        
        # Option 1: Send immediately
        # result = send_drip_message(subscriber, day2_message)
        # if result['success']:
        #     subscriber.current_day = 2
        #     subscriber.schedule_next_message()  # Schedule Day 3
        #     total_advanced += 1
        #     print(f"✅ Day 2 sent immediately to {subscriber.phone_number}")
        
        # Option 2: Schedule for immediate sending (recommended for bulk)
        subscriber.current_day = 1  # Keep at 1 so auto-sender picks it up
        subscriber.next_message_at = timezone.now()  # Schedule immediately
        subscriber.save()
        total_scheduled += 1
        print(f"⏰ Day 2 scheduled for immediate sending to {subscriber.phone_number}")
    
    print(f"\n🎉 Summary:")
    print(f"   📊 Total subscribers processed: {day1_subscribers.count()}")
    print(f"   ⏰ Scheduled for Day 2: {total_scheduled}")
    print(f"   📋 Campaigns processed: {len(campaigns_processed)}")
    
    if total_scheduled > 0:
        print(f"\n🤖 Auto-sender will process these messages within 30 seconds")
        print(f"💡 You can also manually trigger processing via the dashboard")

def send_day2_immediately():
    """Alternative: Send Day 2 messages immediately to all Day 1 subscribers"""
    print("🚀 Sending Day 2 messages immediately...")
    
    day1_subscribers = DripSubscriber.objects.filter(
        status='active',
        current_day=1
    )
    
    print(f"📊 Found {day1_subscribers.count()} subscribers on Day 1")
    
    sent_count = 0
    failed_count = 0
    
    for subscriber in day1_subscribers:
        day2_message = subscriber.campaign.messages.filter(day_number=2, is_active=True).first()
        
        if not day2_message:
            continue
        
        # Check if already sent
        existing = DripMessageLog.objects.filter(
            phone_number=subscriber.phone_number,
            drip_message=day2_message,
            status='sent'
        ).exists()
        
        if existing:
            continue
        
        print(f"📱 Sending Day 2 to {subscriber.first_name} ({subscriber.phone_number})")
        
        result = send_drip_message(subscriber, day2_message)
        
        if result['success']:
            subscriber.current_day = 2
            subscriber.schedule_next_message()  # This will schedule Day 3
            sent_count += 1
            print(f"✅ Day 2 sent to {subscriber.phone_number}")
        else:
            failed_count += 1
            print(f"❌ Failed to send Day 2 to {subscriber.phone_number}: {result['error']}")
    
    print(f"\n🎉 Summary:")
    print(f"   ✅ Successfully sent: {sent_count}")
    print(f"   ❌ Failed: {failed_count}")

if __name__ == "__main__":
    print("=" * 60)
    print("📱 WhatsApp Day 2 Message Advancement Tool")
    print("=" * 60)
    
    choice = input("\nChoose option:\n1. Schedule Day 2 messages (recommended)\n2. Send Day 2 messages immediately\n\nEnter choice (1 or 2): ")
    
    if choice == "1":
        advance_to_day2()
    elif choice == "2":
        send_day2_immediately()
    else:
        print("❌ Invalid choice. Exiting.")
    
    print("\n" + "=" * 60)