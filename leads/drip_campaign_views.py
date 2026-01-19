from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta
import json
import requests
from .models import Lead
from .project_models import Project
from .drip_campaign_models import DripCampaign, DripMessage, DripSubscriber, DripMessageLog
from .drip_auto_sender import auto_sender, send_drip_message

# AI Sensy Configuration
AISENSY_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4ZGVhNzVlYTM3MDcyNTJiYzJhZWY1NyIsIm5hbWUiOiJBQkMgRGlnaXRhbCBJbmMiLCJhcHBOYW1lIjoiQWlTZW5zeSIsImNsaWVudElkIjoiNjhkZWE3NWVhMzcwNzI1MmJjMmFlZjUyIiwiYWN0aXZlUGxhbiI6IkZSRUVfRk9SRVZFUiIsImlhdCI6MTc1OTQyMjMwMn0.GzXAy0qINll2QxsM9Q73B8SHBPeHMXiXZ1ypm8ScNbE"
AISENSY_API_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

def drip_campaigns_dashboard(request):
    """Main dashboard for drip campaigns"""
    campaigns = DripCampaign.objects.all().order_by('-created_at')
    projects = Project.objects.all()
    
    return render(request, 'leads/drip_campaigns_dashboard.html', {
        'campaigns': campaigns,
        'projects': projects,
        'analytics': {
            'total_campaigns': campaigns.count(),
            'active_campaigns': campaigns.filter(status='active').count(),
            'total_subscribers': DripSubscriber.objects.filter(status='active').count(),
            'pending_messages': DripMessageLog.objects.filter(status='pending').count(),
        }
    })

def bulk_subscribe_view(request):
    """View for bulk subscribing leads"""
    campaigns = DripCampaign.objects.filter(status='active').order_by('-created_at')
    
    return render(request, 'leads/bulk_subscribe_leads.html', {
        'campaigns': campaigns
    })

def create_gaur_yamuna_campaign(request):
    """Create the Gaur Yamuna drip campaign with predefined messages"""
    if request.method == 'POST':
        try:
            # Get or create Gaur Yamuna project
            project, created = Project.objects.get_or_create(
                name='Gaur Yamuna',
                defaults={
                    'code': 'gaur_yamuna',
                    'developer': 'Gaur Group',
                    'location': 'Yamuna Expressway'
                }
            )
            
            # Create the drip campaign
            campaign = DripCampaign.objects.create(
                name='Gaur Yamuna Follow-up Sequence',
                project=project,
                description='Complete 9-day WhatsApp follow-up sequence for Gaur Yamuna leads',
                status='active'
            )
            
            # Define the 9-message sequence based on your data
            messages_data = [
            {
                'day': 1,
                'template_name': 'gauryaumanafirsthi',
                'campaign_name': 'gaurfirst',
                'message': 'Hi {{1}}, Thank you for exploring Gaur\'s Ultra-Luxury Residences – Sector 22D, Yamuna Expressway. You\'ve just taken the first big step toward owning a premium home in NCR\'s fastest-growing corridor, where many buyers are quietly eyeing right now. What would you like to explore first? 👇',
                'delay_hours': 0
            },
            {
                'day': 2,
                'template_name': 'gauryaumana_maybelater',
                'campaign_name': 'gauryaumana_LATER',
                'message': 'Hi {{1}}, Top real-estate publications like Economic Times Realty & Moneycontrol Property are calling the Yamuna Expressway belt India\'s next breakthrough zone — all thanks to the Noida International Airport. And Sector 22D sits right in the centre of this growth wave. Want to know why this location is becoming a hotspot?',
                'delay_hours': 24
            },
            {
                'day': 3,
                'template_name': 'gauryaumana_later_2',
                'campaign_name': 'gauryaumana_later2',
                'message': 'Hi {{1}}, Most luxury projects demand heavy upfront payments — but this one is different. Introducing the 20-20-20-20-20 Smart Payment Plan: • 20% — At Booking • 20% — Ground Floor Slab • 20% — 15th Floor Slab • 20% — Super Structure (25th Floor) • 20% — Possession This gives you: ✔️ Low initial investment ✔️ Payments tied to real construction progress ✔️ Safer, cash-flow-friendly investing ✔️ Ideal flexibility for end-users Want to see how much you save upfront?',
                'delay_hours': 24
            },
            {
                'day': 4,
                'template_name': 'gauryaumana_later_3',
                'campaign_name': 'gauryaumana_later3',
                'message': 'While most luxury projects in Noida & Expressway belt are selling at ₹11,000–₹13,000/sq ft, Gaur\'s Sector 22D is launching at just ~₹ 7999/sq ft. That\'s a 30% early-stage advantage. Early buyers are securing their preferred units with an EOI of ₹10,00,000. Would you like to explore pricing in detail?',
                'delay_hours': 24
            },
            {
                'day': 5,
                'template_name': 'gauryaumana_maybelater4',
                'campaign_name': 'gauryaumana_later4',
                'message': 'Hi {{1}}, This project features stand-alone towers, meaning every apartment is a corner unit — full of light, ventilation & privacy. Key highlights: ✔️ 3BHK – 1800 sq ft ✔️ 4BHK – 2400 sq ft ✔️ 11 ft ceiling height ✔️ Only 4 units per floor ✔️ 4 high-speed lifts The architects behind this design were featured in Architectural Digest India. Want to explore the layouts?',
                'delay_hours': 24
            },
            {
                'day': 6,
                'template_name': 'gauryaumana_maybelater5',
                'campaign_name': 'gauryaumana_later5',
                'message': 'Hi {{1}}, Welcome to one of NCR\'s largest lifestyle clubhouses, featuring: ✨ 3-storey glass façade ✨ Spa & wellness zones ✨ Meditation decks ✨ Balling Alley ✨ Coworking Space ✨ Restaurants & Banquet ✨ 2 Indoor Swimming pool (Olympic + Half Olympic) ✨ 3 C\'s room ✨ Indoor games & lounges ✨ Premium fitness spaces ✨ 8 acres of open greens Lifestyle publications like Lifestyle Asia India have already spotlighted this as YEIDA\'s most premium community space. Want to take a closer look?',
                'delay_hours': 24
            },
            {
                'day': 7,
                'template_name': 'gauryaumana_maybelater6',
                'campaign_name': 'gauryaumana_later6',
                'message': 'Hi {{1}}, Welcome to one of NCR\'s largest lifestyle clubhouses, featuring: ✨ 3-storey glass façade ✨ Spa & wellness zones ✨ Meditation decks ✨ Balling Alley ✨ Coworking Space ✨ Restaurants & Banquet ✨ 2 Indoor Swimming pool (Olympic + Half Olympic) ✨ 3 C\'s room ✨ Indoor games & lounges ✨ Premium fitness spaces ✨ 8 acres of open greens Lifestyle publications like Lifestyle Asia India have already spotlighted this as YEIDA\'s most premium community space. Want to take a closer look?',
                'delay_hours': 24
            },
            {
                'day': 8,
                'template_name': 'gauryaumana_later7',
                'campaign_name': 'gauryaumana_later7',
                'message': 'Hi {{1}}, With the Noida International Airport going live soon, the YEIDA zone is becoming a rental goldmine. As shared by ET Realty, Moneycontrol & CNBC Awaaz: ✔️ Airport zones show higher rental yields ✔️ Strong tenant demand (aviation crew, corporates, expats) ✔️ Faster appreciation ✔️ Premium furnished rentals Sector 22D sits exactly at the heart of this upcoming boom. Want to see how this impacts ROI?',
                'delay_hours': 24
            },
            {
                'day': 9,
                'template_name': 'gauryaumana_final',
                'campaign_name': 'gaurfinal',
                'message': 'Hi {{1}}, Buying a home unit rushed decision; it\'s thoughtful. Whenever you want to: ✔️ Explore plans ✔️ Discuss pricing ✔️ Visit the site ✔️ Get one-on-one guidance Just say "Hi" — I\'m always here to assist you. Your dream home is waiting, and so am I 🤝🙂',
                'delay_hours': 24
            }
        ]
            
            # Create drip messages
            for msg_data in messages_data:
                DripMessage.objects.create(
                    campaign=campaign,
                    day_number=msg_data['day'],
                    template_name=msg_data['template_name'],
                    campaign_name=msg_data['campaign_name'],
                    message_text=msg_data['message'],
                    api_key=AISENSY_API_KEY,
                    template_params=['$FirstName'],
                    fallback_params={'FirstName': 'user'},
                    delay_hours=msg_data['delay_hours']
                )
            
            messages.success(request, f'Gaur Yamuna drip campaign created with {len(messages_data)} messages (9-day sequence)!')
            
            # Return JSON for AJAX requests
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f'Gaur Yamuna campaign created with {len(messages_data)} messages',
                    'campaign_id': campaign.id
                })
            
            return redirect('drip_campaigns_dashboard')
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error: {str(e)}')
            return redirect('drip_campaigns_dashboard')
    
    return render(request, 'leads/create_gaur_yamuna_campaign.html')

@csrf_exempt
def subscribe_lead_to_drip(request):
    """Subscribe a lead to a drip campaign"""
    if request.method == 'POST':
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        campaign_id = data.get('campaign_id')
        
        print(f"[DRIP SUBSCRIBE] Lead {lead_id} to Campaign {campaign_id}")
        
        try:
            lead = get_object_or_404(Lead, id=lead_id)
            campaign = get_object_or_404(DripCampaign, id=campaign_id)
            
            print(f"[DRIP SUBSCRIBE] Found lead: {lead.full_name} ({lead.phone_number})")
            print(f"[DRIP SUBSCRIBE] Found campaign: {campaign.name}")
            
            # Check if already subscribed or recently messaged
            existing_subscription = DripSubscriber.objects.filter(
                campaign=campaign,
                lead=lead
            ).first()
            
            recent_message = DripMessageLog.objects.filter(
                phone_number=lead.phone_number,
                drip_message__campaign=campaign,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).first()
            
            if existing_subscription:
                print(f"[DRIP SUBSCRIBE] Already subscribed")
                return JsonResponse({
                    'success': False,
                    'error': 'Lead is already subscribed to this campaign'
                })
            
            if recent_message:
                print(f"[DRIP SUBSCRIBE] Recent message sent in last 24h")
                return JsonResponse({
                    'success': False,
                    'error': 'Message already sent to this number in last 24 hours'
                })
            
            # Create subscription
            subscriber = DripSubscriber.objects.create(
                campaign=campaign,
                lead=lead,
                phone_number=lead.phone_number,
                first_name=lead.full_name or lead.first_name or 'User',
                status='active'
            )
            
            print(f"[DRIP SUBSCRIBE] Created subscriber: {subscriber.id}")
            
            # Schedule first message (Day 1)
            first_message = campaign.messages.filter(day_number=1, is_active=True).first()
            if first_message:
                print(f"[DRIP SUBSCRIBE] Found first message: Day {first_message.day_number}")
                # Send immediately or schedule based on delay
                if first_message.total_delay_minutes == 0:
                    print(f"[DRIP SUBSCRIBE] Sending immediately")
                    # Send immediately
                    result = send_drip_message(subscriber, first_message)
                    if result['success']:
                        subscriber.current_day = 1
                        subscriber.schedule_next_message()
                        print(f"[DRIP SUBSCRIBE] First message sent, next scheduled")
                else:
                    print(f"[DRIP SUBSCRIBE] Scheduling for {first_message.total_delay_minutes} minutes")
                    # Schedule for later
                    subscriber.next_message_at = timezone.now() + timedelta(minutes=first_message.total_delay_minutes)
                    subscriber.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Lead subscribed to {campaign.name}',
                'subscriber_id': subscriber.id
            })
            
        except Exception as e:
            print(f"[DRIP SUBSCRIBE] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def bulk_subscribe_leads(request):
    """Bulk subscribe multiple leads to a drip campaign"""
    if request.method == 'POST':
        data = json.loads(request.body)
        lead_ids = data.get('lead_ids', [])
        campaign_id = data.get('campaign_id')
        custom_delays = data.get('custom_delays', {})
        
        print(f"[BULK SUBSCRIBE] {len(lead_ids)} leads to campaign {campaign_id}")
        
        try:
            campaign = get_object_or_404(DripCampaign, id=campaign_id)
            leads = Lead.objects.filter(id__in=lead_ids)
            
            print(f"[BULK SUBSCRIBE] Campaign: {campaign.name}")
            print(f"[BULK SUBSCRIBE] Found {leads.count()} leads")
            
            # Update campaign message delays if provided
            if custom_delays:
                print(f"[BULK SUBSCRIBE] Updating delays: {custom_delays}")
                for day_num, delay_data in custom_delays.items():
                    try:
                        message = campaign.messages.get(day_number=int(day_num))
                        message.delay_hours = delay_data.get('hours', 0)
                        message.delay_minutes = delay_data.get('minutes', 0)
                        message.save()
                        print(f"[BULK SUBSCRIBE] Updated Day {day_num}: {message.delay_hours}h {message.delay_minutes}m")
                    except DripMessage.DoesNotExist:
                        continue
            
            subscribed_count = 0
            already_subscribed = 0
            
            # Get Day 1 message to check for existing sends
            first_message = campaign.messages.filter(day_number=1, is_active=True).first()
            
            for lead in leads:
                # Check if Day 1 message already sent to this phone number
                if first_message:
                    already_sent = DripMessageLog.objects.filter(
                        phone_number=lead.phone_number,
                        drip_message=first_message,
                        status='sent'
                    ).exists()
                    
                    if already_sent:
                        already_subscribed += 1
                        print(f"[BULK SUBSCRIBE] Skipping {lead.phone_number} - Day 1 already sent")
                        continue
                
                # Check if already subscribed
                if DripSubscriber.objects.filter(campaign=campaign, lead=lead).exists():
                    already_subscribed += 1
                    print(f"[BULK SUBSCRIBE] Skipping {lead.phone_number} - already subscribed")
                    continue
                
                # Create subscription
                subscriber = DripSubscriber.objects.create(
                    campaign=campaign,
                    lead=lead,
                    phone_number=lead.phone_number,
                    first_name=lead.full_name or lead.first_name or 'User',
                    status='active',
                    current_day=0
                )
                
                print(f"[BULK SUBSCRIBE] ✅ Subscribed {subscriber.first_name} ({subscriber.phone_number}) - Lead ID: {lead.id}")
                
                # Schedule Day 1 message (don't send immediately in bulk)
                if first_message:
                    # Always schedule, never send immediately in bulk operations
                    print(f"[BULK SUBSCRIBE] Scheduling Day 1 for {subscriber.phone_number} in {first_message.total_delay_minutes} minutes")
                    subscriber.next_message_at = timezone.now() + timedelta(minutes=first_message.total_delay_minutes)
                    subscriber.save()
                
                subscribed_count += 1
            
            print(f"[BULK SUBSCRIBE] Complete: {subscribed_count} subscribed, {already_subscribed} already subscribed")
            
            # Auto-start the sender if not already running
            if subscribed_count > 0:
                try:
                    auto_sender.start()
                    print(f"[BULK SUBSCRIBE] Auto-started message sender")
                except:
                    pass  # Already running
            
            return JsonResponse({
                'success': True,
                'subscribed': subscribed_count,
                'already_subscribed': already_subscribed,
                'message': f'Subscribed {subscribed_count} leads to {campaign.name}'
            })
            
        except Exception as e:
            print(f"[BULK SUBSCRIBE] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def leads_api(request):
    """API to get leads for selection"""
    search = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    per_page = 20
    
    leads = Lead.objects.all()
    
    if search:
        leads = leads.filter(
            Q(full_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(email__icontains=search)
        )
    
    total = leads.count()
    leads = leads[(page-1)*per_page:page*per_page]
    
    leads_data = []
    for lead in leads:
        leads_data.append({
            'id': lead.id,
            'name': lead.full_name or lead.first_name or f'Lead {lead.id}',
            'phone': lead.phone_number,
            'email': lead.email,
            'created': lead.created_time.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'leads': leads_data,
        'total': total,
        'page': page,
        'has_next': page * per_page < total
    })

def send_drip_message_old(subscriber, drip_message):
    """Send a single drip message via AI Sensy"""
    print(f"[DRIP SEND] Starting send to {subscriber.phone_number} - Day {drip_message.day_number}")
    
    try:
        # Clean phone number
        clean_phone = subscriber.phone_number.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
        if not clean_phone.startswith('91'):
            clean_phone = f"91{clean_phone}"
        
        print(f"[DRIP SEND] Cleaned phone: {clean_phone}")
        
        # Prepare message text
        message_text = drip_message.message_text.replace('{{1}}', subscriber.first_name)
        print(f"[DRIP SEND] Message text prepared for {subscriber.first_name}")
        
        # Build AI Sensy payload (simplified format)
        payload = {
            "apiKey": drip_message.api_key,
            "campaignName": drip_message.campaign_name,
            "destination": clean_phone,
            "userName": subscriber.first_name,
            "templateParams": [subscriber.first_name],
            "source": "new-landing-page form",
            "media": {},
            "buttons": [],
            "carouselCards": [],
            "location": {},
            "paramsFallbackValue": {
                "FirstName": subscriber.first_name
            }
        }
        
        print(f"[DRIP SEND] Payload prepared: {payload['campaignName']} to {payload['destination']}")
        print(f"[DRIP SEND] Full payload: {json.dumps(payload, indent=2)}")
        
        # Create message log
        message_log = DripMessageLog.objects.create(
            subscriber=subscriber,
            drip_message=drip_message,
            phone_number=subscriber.phone_number,
            recipient_name=subscriber.first_name,
            final_message_text=message_text,
            scheduled_at=timezone.now(),
            status='pending'
        )
        
        print(f"[DRIP SEND] Message log created: {message_log.id}")
        
        # Send via AI Sensy API
        try:
            print(f"[DRIP SEND] Sending API request to {AISENSY_API_URL}")
            response = requests.post(
                AISENSY_API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"[DRIP SEND] API Response: {response.status_code} - {response.text[:200]}")
            
            if response.status_code == 200:
                message_log.status = 'sent'
                message_log.sent_at = timezone.now()
                message_log.api_response = {
                    'status_code': response.status_code,
                    'response': response.text,
                    'payload_sent': payload
                }
                
                # Update drip message analytics
                drip_message.sent_count += 1
                drip_message.save()
                
                print(f"[DRIP SEND] SUCCESS: Message sent successfully")
                success = True
                error = None
            else:
                message_log.status = 'failed'
                message_log.failed_at = timezone.now()
                message_log.error_message = f'API Error {response.status_code}: {response.text}'
                message_log.api_response = {
                    'status_code': response.status_code,
                    'response': response.text,
                    'payload_sent': payload
                }
                
                drip_message.failed_count += 1
                drip_message.save()
                
                print(f"[DRIP SEND] FAILED: API Error {response.status_code}")
                success = False
                error = message_log.error_message
                
        except Exception as api_error:
            message_log.status = 'failed'
            message_log.failed_at = timezone.now()
            message_log.error_message = f'API Exception: {str(api_error)}'
            message_log.api_response = {'error': str(api_error), 'payload_sent': payload}
            
            drip_message.failed_count += 1
            drip_message.save()
            
            print(f"[DRIP SEND] EXCEPTION: {str(api_error)}")
            success = False
            error = str(api_error)
        
        message_log.save()
        
        return {
            'success': success,
            'message_log_id': message_log.id,
            'error': error
        }
        
    except Exception as e:
        print(f"[DRIP SEND] CRITICAL ERROR: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@csrf_exempt
def process_pending_messages(request):
    """Process all pending drip messages"""
    if request.method == 'POST':
        print(f"[PROCESS PENDING] Starting to process pending messages")
        
        try:
            # Get all subscribers with pending messages
            now = timezone.now()
            subscribers_ready = DripSubscriber.objects.filter(
                status='active',
                next_message_at__lte=now
            )
            
            print(f"[PROCESS PENDING] Found {subscribers_ready.count()} subscribers ready for messages")
            
            processed_count = 0
            success_count = 0
            
            for subscriber in subscribers_ready:
                next_message = subscriber.get_next_message()
                if next_message:
                    print(f"[PROCESS PENDING] Processing {subscriber.phone_number} - Day {next_message.day_number}")
                    result = send_drip_message(subscriber, next_message)
                    processed_count += 1
                    
                    if result['success']:
                        success_count += 1
                        subscriber.current_day = next_message.day_number
                        subscriber.schedule_next_message()
                        print(f"[PROCESS PENDING] SUCCESS: {subscriber.phone_number} - Day {next_message.day_number}")
                    else:
                        # Log the error but continue processing
                        print(f"[PROCESS PENDING] FAILED: {subscriber.phone_number} - {result['error']}")
                else:
                    print(f"[PROCESS PENDING] No next message for {subscriber.phone_number}")
            
            print(f"[PROCESS PENDING] Complete: {success_count}/{processed_count} successful")
            
            return JsonResponse({
                'success': True,
                'processed': processed_count,
                'successful': success_count,
                'failed': processed_count - success_count
            })
            
        except Exception as e:
            print(f"[PROCESS PENDING] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def campaign_detail(request, campaign_id):
    """View campaign details and subscribers"""
    campaign = get_object_or_404(DripCampaign, id=campaign_id)
    messages = campaign.messages.all().order_by('day_number')
    subscribers = campaign.subscribers.all().order_by('-subscribed_at')
    projects = Project.objects.all().order_by('name')
    
    # Analytics
    total_subscribers = subscribers.count()
    active_subscribers = subscribers.filter(status='active').count()
    completed_subscribers = subscribers.filter(status='completed').count()
    
    # Message analytics
    total_sent = sum(msg.sent_count for msg in messages)
    total_failed = sum(msg.failed_count for msg in messages)
    
    analytics = {
        'total_subscribers': total_subscribers,
        'active_subscribers': active_subscribers,
        'completed_subscribers': completed_subscribers,
        'total_sent': total_sent,
        'total_failed': total_failed,
        'success_rate': (total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0
    }
    
    return render(request, 'leads/drip_campaign_detail.html', {
        'campaign': campaign,
        'messages': messages,
        'subscribers': subscribers[:50],  # Limit for performance
        'analytics': analytics,
        'projects': projects
    })

@csrf_exempt
def test_drip_message(request):
    """Test a single drip message"""
    if request.method == 'POST':
        data = json.loads(request.body)
        message_id = data.get('message_id')
        test_phone = data.get('test_phone')
        test_name = data.get('test_name', 'Test User')
        
        print(f"[DRIP TEST] Testing message ID: {message_id} to {test_phone}")
        
        try:
            drip_message = get_object_or_404(DripMessage, id=message_id)
            print(f"[DRIP TEST] Found message: Day {drip_message.day_number} - {drip_message.template_name}")
            
            # Get or create a test lead (use lead_id as unique identifier)
            test_lead, created = Lead.objects.get_or_create(
                lead_id=f'test_{test_phone}',
                defaults={
                    'phone_number': test_phone,
                    'full_name': test_name,
                    'email': f'test_{test_phone}@example.com',
                    'form_name': 'Test Form',
                    'source': 'Test',
                    'created_time': timezone.now()
                }
            )
            
            # Create and save a temporary subscriber for testing
            temp_subscriber = DripSubscriber.objects.create(
                campaign=drip_message.campaign,
                lead=test_lead,
                phone_number=test_phone,
                first_name=test_name,
                status='active'
            )
            print(f"[DRIP TEST] Created temp subscriber: {temp_subscriber.id} for lead: {test_lead.id}")
            
            result = send_drip_message(temp_subscriber, drip_message)
            print(f"[DRIP TEST] Send result: {result}")
            
            # Clean up temp subscriber
            temp_subscriber.delete()
            print(f"[DRIP TEST] Cleaned up temp subscriber")
            
            return JsonResponse({
                'success': result['success'],
                'message': f'Test message sent to {test_phone}' if result['success'] else f'Failed: {result["error"]}'
            })
            
        except Exception as e:
            print(f"[DRIP TEST] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def drip_analytics(request):
    """Analytics dashboard for drip campaigns"""
    campaigns = DripCampaign.objects.all()
    
    # Overall analytics
    total_campaigns = campaigns.count()
    total_subscribers = DripSubscriber.objects.count()
    active_subscribers = DripSubscriber.objects.filter(status='active').count()
    total_messages_sent = DripMessageLog.objects.filter(status='sent').count()
    
    # Campaign performance
    campaign_stats = []
    for campaign in campaigns:
        subscribers = campaign.subscribers.all()
        message_logs = DripMessageLog.objects.filter(subscriber__campaign=campaign)
        
        campaign_stats.append({
            'campaign': campaign,
            'subscribers': subscribers.count(),
            'active_subscribers': subscribers.filter(status='active').count(),
            'completed_subscribers': subscribers.filter(status='completed').count(),
            'messages_sent': message_logs.filter(status='sent').count(),
            'messages_failed': message_logs.filter(status='failed').count(),
        })
    
    analytics = {
        'total_campaigns': total_campaigns,
        'total_subscribers': total_subscribers,
        'active_subscribers': active_subscribers,
        'total_messages_sent': total_messages_sent,
        'campaign_stats': campaign_stats
    }
    
    return render(request, 'leads/drip_analytics.html', {
        'analytics': analytics
    })

@csrf_exempt
def unsubscribe_lead_from_drip(request):
    """Unsubscribe a lead from a drip campaign"""
    if request.method == 'POST':
        data = json.loads(request.body)
        subscriber_id = data.get('subscriber_id')
        
        print(f"[DRIP UNSUBSCRIBE] Unsubscribing subscriber ID: {subscriber_id}")
        
        try:
            subscriber = get_object_or_404(DripSubscriber, id=subscriber_id)
            
            print(f"[DRIP UNSUBSCRIBE] Found subscriber: {subscriber.phone_number} from {subscriber.campaign.name}")
            
            # Delete the subscriber
            campaign_name = subscriber.campaign.name
            phone_number = subscriber.phone_number
            subscriber.delete()
            
            print(f"[DRIP UNSUBSCRIBE] Successfully unsubscribed {phone_number} from {campaign_name}")
            
            return JsonResponse({
                'success': True,
                'message': f'Lead unsubscribed from {campaign_name}'
            })
            
        except Exception as e:
            print(f"[DRIP UNSUBSCRIBE] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def bulk_unsubscribe_leads(request):
    """Bulk unsubscribe multiple leads from a drip campaign"""
    if request.method == 'POST':
        data = json.loads(request.body)
        campaign_id = data.get('campaign_id')
        
        print(f"[BULK UNSUBSCRIBE] Unsubscribing all leads from campaign {campaign_id}")
        
        try:
            campaign = get_object_or_404(DripCampaign, id=campaign_id)
            subscribers = campaign.subscribers.all()
            
            count = subscribers.count()
            print(f"[BULK UNSUBSCRIBE] Found {count} subscribers to remove")
            
            # Delete all subscribers
            subscribers.delete()
            
            print(f"[BULK UNSUBSCRIBE] Successfully removed {count} subscribers from {campaign.name}")
            
            return JsonResponse({
                'success': True,
                'message': f'Removed {count} subscribers from {campaign.name}',
                'count': count
            })
            
        except Exception as e:
            print(f"[BULK UNSUBSCRIBE] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def fix_campaign_names(request):
    """Fix campaign names in existing messages"""
    if request.method == 'POST':
        print(f"[FIX CAMPAIGNS] Fixing campaign names")
        
        try:
            # Update Day 1 message to use gaurfirst
            day1_messages = DripMessage.objects.filter(day_number=1)
            for msg in day1_messages:
                msg.template_name = 'gauryaumanafirsthi'
                msg.campaign_name = 'gaurfirst'
                msg.message_text = 'Hi {{1}}, Thank you for exploring Gaur\'s Ultra-Luxury Residences – Sector 22D, Yamuna Expressway. You\'ve just taken the first big step toward owning a premium home in NCR\'s fastest-growing corridor, where many buyers are quietly eyeing right now. What would you like to explore first? 👇'
                msg.save()
                print(f"[FIX CAMPAIGNS] Updated Day 1 message to gaurfirst")
            
            return JsonResponse({
                'success': True,
                'message': f'Fixed {day1_messages.count()} Day 1 messages'
            })
            
        except Exception as e:
            print(f"[FIX CAMPAIGNS] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def auto_process_drip_messages(request):
    """Auto-process drip messages - call this every 5 minutes"""
    print(f"[AUTO DRIP] Starting auto-process at {timezone.now()}")
    
    try:
        # Get all subscribers with pending messages
        now = timezone.now()
        subscribers_ready = DripSubscriber.objects.filter(
            status='active',
            next_message_at__lte=now
        )
        
        print(f"[AUTO DRIP] Found {subscribers_ready.count()} subscribers ready")
        
        processed = 0
        successful = 0
        
        for subscriber in subscribers_ready:
            next_message = subscriber.get_next_message()
            if next_message:
                result = send_drip_message(subscriber, next_message)
                processed += 1
                
                if result['success']:
                    successful += 1
                    subscriber.current_day = next_message.day_number
                    subscriber.schedule_next_message()
        
        print(f"[AUTO DRIP] Complete: {successful}/{processed} successful")
        
        return JsonResponse({
            'success': True,
            'processed': processed,
            'successful': successful
        })
        
    except Exception as e:
        print(f"[AUTO DRIP] Error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
@csrf_exempt
def start_auto_sender(request):
    """Start the automatic drip message sender"""
    if request.method == 'POST':
        try:
            auto_sender.start()
            return JsonResponse({
                'success': True,
                'message': 'Auto sender started'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def stop_auto_sender(request):
    """Stop the automatic drip message sender"""
    if request.method == 'POST':
        try:
            auto_sender.stop()
            return JsonResponse({
                'success': True,
                'message': 'Auto sender stopped'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Invalid request'})
@csrf_exempt
def delete_campaign(request):
    """Delete a drip campaign"""
    if request.method == 'POST':
        data = json.loads(request.body)
        campaign_id = data.get('campaign_id')
        
        print(f"[DELETE CAMPAIGN] Deleting campaign {campaign_id}")
        
        try:
            campaign = get_object_or_404(DripCampaign, id=campaign_id)
            campaign_name = campaign.name
            
            # Delete all related data
            campaign.delete()
            
            print(f"[DELETE CAMPAIGN] Successfully deleted {campaign_name}")
            
            return JsonResponse({
                'success': True,
                'message': f'Campaign {campaign_name} deleted successfully'
            })
            
        except Exception as e:
            print(f"[DELETE CAMPAIGN] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def subscribe_project_leads(request):
    """Subscribe all leads from a project to a drip campaign"""
    if request.method == 'POST':
        data = json.loads(request.body)
        project_id = data.get('project_id')
        campaign_id = data.get('campaign_id')
        
        print(f"[PROJECT SUBSCRIBE] Project {project_id} to Campaign {campaign_id}")
        
        try:
            project = get_object_or_404(Project, id=project_id)
            campaign = get_object_or_404(DripCampaign, id=campaign_id)
            
            # Get all leads with phone numbers from this project
            leads = project.get_leads().filter(
                phone_number__isnull=False
            ).exclude(phone_number='')
            
            total_leads = leads.count()
            print(f"[PROJECT SUBSCRIBE] Found {total_leads} leads in {project.name}")
            
            subscribed_count = 0
            already_subscribed = 0
            
            # Get Day 1 message to check for existing sends
            first_message = campaign.messages.filter(day_number=1, is_active=True).first()
            
            for lead in leads:
                # Check if Day 1 message already sent to this phone number
                if first_message:
                    already_sent = DripMessageLog.objects.filter(
                        phone_number=lead.phone_number,
                        drip_message=first_message,
                        status='sent'
                    ).exists()
                    
                    if already_sent:
                        already_subscribed += 1
                        print(f"[PROJECT SUBSCRIBE] Skipping {lead.phone_number} - Day 1 already sent")
                        continue
                
                # Check if already subscribed
                if DripSubscriber.objects.filter(campaign=campaign, lead=lead).exists():
                    already_subscribed += 1
                    print(f"[PROJECT SUBSCRIBE] Skipping {lead.phone_number} - already subscribed")
                    continue
                
                # Create subscription
                subscriber = DripSubscriber.objects.create(
                    campaign=campaign,
                    lead=lead,
                    phone_number=lead.phone_number,
                    first_name=lead.full_name or 'User',
                    status='active',
                    current_day=0
                )
                
                print(f"[PROJECT SUBSCRIBE] ✅ Subscribed {lead.full_name} ({lead.phone_number})")
                
                # Schedule Day 1 message (don't send immediately)
                if first_message:
                    # Always schedule, never send immediately in bulk
                    subscriber.next_message_at = timezone.now() + timedelta(minutes=first_message.total_delay_minutes)
                    subscriber.save()
                
                subscribed_count += 1
            
            print(f"[PROJECT SUBSCRIBE] Complete: {subscribed_count} subscribed, {already_subscribed} already subscribed")
            
            # Auto-start the sender
            if subscribed_count > 0:
                try:
                    auto_sender.start()
                except:
                    pass
            
            return JsonResponse({
                'success': True,
                'subscribed': subscribed_count,
                'already_subscribed': already_subscribed,
                'total_leads': total_leads,
                'message': f'Subscribed {subscribed_count} leads from {project.name} to {campaign.name}'
            })
            
        except Exception as e:
            print(f"[PROJECT SUBSCRIBE] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def advance_to_day2(request):
    """Send Day 2 messages to subscribers who have received Day 1"""
    if request.method == 'POST':
        data = json.loads(request.body)
        campaign_id = data.get('campaign_id')
        
        print(f"[SEND DAY2] Sending Day 2 messages for campaign {campaign_id}")
        
        try:
            if campaign_id:
                campaign = get_object_or_404(DripCampaign, id=campaign_id)
                # Find subscribers who have received Day 1 but not Day 2
                day1_message = campaign.messages.filter(day_number=1, is_active=True).first()
                day2_message = campaign.messages.filter(day_number=2, is_active=True).first()
                
                if not day1_message or not day2_message:
                    return JsonResponse({
                        'success': False,
                        'error': 'Day 1 or Day 2 message not found'
                    })
                
                # Get phone numbers that received Day 1
                day1_sent_phones = set(DripMessageLog.objects.filter(
                    drip_message=day1_message,
                    status='sent'
                ).values_list('phone_number', flat=True))
                
                # Get phone numbers that already received Day 2
                day2_sent_phones = set(DripMessageLog.objects.filter(
                    drip_message=day2_message,
                    status='sent'
                ).values_list('phone_number', flat=True))
                
                # Find phones that need Day 2 (received Day 1 but not Day 2)
                phones_need_day2 = day1_sent_phones - day2_sent_phones
                
                print(f"[SEND DAY2] Day 1 sent to: {len(day1_sent_phones)} phones")
                print(f"[SEND DAY2] Day 2 already sent to: {len(day2_sent_phones)} phones")
                print(f"[SEND DAY2] Need Day 2: {len(phones_need_day2)} phones")
                
                if not phones_need_day2:
                    return JsonResponse({
                        'success': False,
                        'error': 'No subscribers need Day 2 messages (all have already received it)'
                    })
                
                # Get active subscribers for these phone numbers
                subscribers_need_day2 = DripSubscriber.objects.filter(
                    campaign=campaign,
                    status='active',
                    phone_number__in=phones_need_day2
                )
                
                print(f"[SEND DAY2] Found {subscribers_need_day2.count()} active subscribers needing Day 2")
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Campaign ID required'
                })
            
            scheduled_count = 0
            
            for subscriber in subscribers_need_day2:
                # Force schedule Day 2 message immediately
                subscriber.current_day = 1  # Set to 1 so get_next_message() returns Day 2
                subscriber.next_message_at = timezone.now()
                subscriber.save()
                scheduled_count += 1
                print(f"[SEND DAY2] ✅ Scheduled Day 2 for {subscriber.first_name} ({subscriber.phone_number})")
            
            print(f"[SEND DAY2] Complete: {scheduled_count} scheduled for Day 2")
            
            # Start auto-sender to process immediately
            try:
                auto_sender.start()
                print(f"[SEND DAY2] Auto-sender started")
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'scheduled': scheduled_count,
                'already_sent': len(day2_sent_phones),
                'message': f'Scheduled Day 2 messages for {scheduled_count} subscribers. Auto-sender will process within 30 seconds.'
            })
            
        except Exception as e:
            print(f"[SEND DAY2] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def send_specific_day_message(request):
    """Send a specific day message to subscribers who haven't received it yet"""
    if request.method == 'POST':
        data = json.loads(request.body)
        campaign_id = data.get('campaign_id')
        target_day = int(data.get('target_day', 2))
        
        print(f"[SEND DAY{target_day}] Sending Day {target_day} messages for campaign {campaign_id}")
        
        try:
            campaign = get_object_or_404(DripCampaign, id=campaign_id)
            target_message = campaign.messages.filter(day_number=target_day, is_active=True).first()
            
            if not target_message:
                return JsonResponse({
                    'success': False,
                    'error': f'Day {target_day} message not found'
                })
            
            # Get phone numbers that already received this day's message
            already_sent_phones = set(DripMessageLog.objects.filter(
                drip_message=target_message,
                status='sent'
            ).values_list('phone_number', flat=True))
            
            # Get all active subscribers who haven't received this message
            subscribers_need_message = DripSubscriber.objects.filter(
                campaign=campaign,
                status='active'
            ).exclude(phone_number__in=already_sent_phones)
            
            print(f"[SEND DAY{target_day}] Found {subscribers_need_message.count()} subscribers needing Day {target_day}")
            print(f"[SEND DAY{target_day}] Already sent to {len(already_sent_phones)} phones")
            
            if subscribers_need_message.count() == 0:
                return JsonResponse({
                    'success': False,
                    'error': f'No subscribers need Day {target_day} messages (all have already received it)'
                })
            
            scheduled_count = 0
            
            for subscriber in subscribers_need_message:
                # Set current_day to target_day-1 so get_next_message() returns target_day
                subscriber.current_day = target_day - 1
                subscriber.next_message_at = timezone.now()
                subscriber.save()
                scheduled_count += 1
                print(f"[SEND DAY{target_day}] ✅ Scheduled Day {target_day} for {subscriber.first_name} ({subscriber.phone_number})")
            
            print(f"[SEND DAY{target_day}] Complete: {scheduled_count} scheduled for Day {target_day}")
            
            # Start auto-sender
            try:
                auto_sender.start()
                print(f"[SEND DAY{target_day}] Auto-sender started")
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'scheduled': scheduled_count,
                'already_sent': len(already_sent_phones),
                'target_day': target_day,
                'message': f'Scheduled Day {target_day} messages for {scheduled_count} subscribers. Auto-sender will process within 30 seconds.'
            })
            
        except Exception as e:
            print(f"[SEND DAY{target_day}] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def switch_campaign_variant(request):
    """Switch between campaign variants (e.g., spjday1 to spjday10)"""
    if request.method == 'POST':
        data = json.loads(request.body)
        variant_group = data.get('variant_group')
        active_campaign_id = data.get('active_campaign_id')
        
        print(f"[SWITCH VARIANT] Switching {variant_group} to campaign {active_campaign_id}")
        
        try:
            # Get all campaigns in this variant group
            campaigns = DripCampaign.objects.filter(variant_group=variant_group)
            
            if not campaigns.exists():
                return JsonResponse({
                    'success': False,
                    'error': f'No campaigns found for variant group: {variant_group}'
                })
            
            # Deactivate all variants in this group
            campaigns.update(is_active_variant=False)
            print(f"[SWITCH VARIANT] Deactivated all {campaigns.count()} variants")
            
            # Activate the selected campaign
            active_campaign = get_object_or_404(DripCampaign, id=active_campaign_id, variant_group=variant_group)
            active_campaign.is_active_variant = True
            active_campaign.save()
            
            print(f"[SWITCH VARIANT] Activated: {active_campaign.name}")
            
            return JsonResponse({
                'success': True,
                'message': f'Switched to {active_campaign.name}',
                'active_campaign': active_campaign.name
            })
            
        except Exception as e:
            print(f"[SWITCH VARIANT] Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def get_campaign_variants(request):
    """Get all variants for a campaign group"""
    variant_group = request.GET.get('variant_group')
    
    if not variant_group:
        return JsonResponse({'success': False, 'error': 'variant_group required'})
    
    try:
        campaigns = DripCampaign.objects.filter(variant_group=variant_group).order_by('name')
        
        variants = []
        for campaign in campaigns:
            variants.append({
                'id': campaign.id,
                'name': campaign.name,
                'is_active': campaign.is_active_variant,
                'subscribers': campaign.subscribers.count(),
                'messages_sent': sum(msg.sent_count for msg in campaign.messages.all())
            })
        
        active_campaign = campaigns.filter(is_active_variant=True).first()
        
        return JsonResponse({
            'success': True,
            'variants': variants,
            'active_campaign_id': active_campaign.id if active_campaign else None,
            'active_campaign_name': active_campaign.name if active_campaign else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def create_spj_10day_campaigns(request):
    """Create 10 SPJ day campaigns with variant support"""
    if request.method == 'POST':
        try:
            # Get or create SPJ project
            project, created = Project.objects.get_or_create(
                name='SPJ',
                defaults={
                    'code': 'spj',
                    'developer': 'SPJ',
                    'location': 'SPJ Location'
                }
            )
            
            # 10-day campaign data
            campaigns_data = [
                {'day': 1, 'destination': '919999929832'},
                {'day': 2, 'destination': '919999929832'},
                {'day': 3, 'destination': '919999929832'},
                {'day': 4, 'destination': '919999929832'},
                {'day': 5, 'destination': '919999929832'},
                {'day': 6, 'destination': '919999929832'},
                {'day': 7, 'destination': '919999929832'},
                {'day': 8, 'destination': '919169739813'},
                {'day': 9, 'destination': '919999929832'},
                {'day': 10, 'destination': '919999929832'},
            ]
            
            created_campaigns = []
            
            for campaign_data in campaigns_data:
                day = campaign_data['day']
                destination = campaign_data['destination']
                
                # Create campaign
                campaign = DripCampaign.objects.create(
                    name=f'SPJ Day {day}',
                    project=project,
                    description=f'SPJ {day}-day follow-up campaign',
                    status='active',
                    variant_group='spjday',
                    is_active_variant=(day == 1)  # Only Day 1 is active by default
                )
                
                # Create single message for this day
                DripMessage.objects.create(
                    campaign=campaign,
                    day_number=1,
                    template_name=f'spjday{day}',
                    campaign_name=f'spjday{day}',
                    message_text=f'Hi {{{{1}}}}, This is Day {day} message from SPJ campaign.',
                    api_key=AISENSY_API_KEY,
                    template_params=['$FirstName'],
                    fallback_params={'FirstName': 'user'},
                    delay_hours=0
                )
                
                created_campaigns.append(campaign)
                print(f"[CREATE SPJ] Created campaign: {campaign.name}")
            
            messages.success(request, f'Created 10 SPJ day campaigns with variant switching support!')
            
            # Return JSON for AJAX requests
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f'Created 10 SPJ day campaigns',
                    'campaigns_count': len(created_campaigns)
                })
            
            return redirect('drip_campaigns_dashboard')
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error: {str(e)}')
            return redirect('drip_campaigns_dashboard')
    
    return render(request, 'leads/create_spj_campaigns.html')
