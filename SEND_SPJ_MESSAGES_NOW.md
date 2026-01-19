# SPJ Drip Campaign - Send Messages Now!

## Problem
You subscribed 447 leads to SPJ Day 1, but messages aren't being sent automatically.

## Solution
The drip campaign system needs a **background process** to send messages. Here's how to trigger it:

### Option 1: Manual Trigger (Quick - Do This Now!)

Open your browser and go to:
```
http://localhost:8001/drip-campaigns/process-pending/
```

Or use curl:
```bash
curl -X POST http://localhost:8001/drip-campaigns/process-pending/
```

This will immediately send all 447 pending messages!

### Option 2: Start Auto-Sender (Automatic)

Go to:
```
http://localhost:8001/drip-campaigns/
```

Click "Start Auto-Sender" button

This will automatically process messages every 30 seconds.

### Option 3: Command Line

```bash
cd d:\AI-proto\CRM\drip
python manage.py shell
```

Then run:
```python
from leads.drip_auto_sender import auto_sender
auto_sender.start()
print("Auto-sender started!")
```

---

## Check Message Status

After triggering, check:
```
http://localhost:8001/drip-campaigns/5/
```

You should see:
- Subscribers: 447
- Messages Sent: 447 (or close to it)
- Failed: 0 (hopefully!)

---

## Why Messages Weren't Sent Automatically

The drip campaign system requires a background process to:
1. Check for subscribers with `next_message_at <= now`
2. Send the message via AISensy API
3. Schedule the next message

This process needs to be triggered either:
- Manually via `/drip-campaigns/process-pending/`
- Automatically via auto-sender
- Via cron job (production)

---

## Quick Test

1. Go to: `http://localhost:8001/drip-campaigns/process-pending/`
2. Wait 10-30 seconds
3. Check: `http://localhost:8001/drip-campaigns/5/`
4. You should see messages sent!

---

## For Production

Add to crontab:
```bash
*/5 * * * * cd /path/to/crm && python manage.py shell -c "from leads.drip_auto_sender import auto_sender; auto_sender.process_once()"
```

Or use Celery for better control.
