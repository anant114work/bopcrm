# Create WhatsApp Templates for SPJ

## Quick Fix - Run This Now!

```bash
python manage.py shell
```

Then paste this:

```python
from leads.project_models import Project
from leads.whatsapp_models import WhatsAppTemplate

# Get SPJ project
spj = Project.objects.get(name='SPJ')

# Template 1: Welcome Message
WhatsAppTemplate.objects.create(
    project=spj,
    name='SPJ Welcome',
    template_type='TEXT',
    category='welcome',
    message_text='Hi {name}, thank you for your interest in SPJ Vedatam! Our team will contact you shortly.',
    api_key='YOUR_AISENSY_API_KEY_HERE',
    campaign_name='spj_welcome',
    order=1,
    is_active=True
)

# Template 2: Follow-up
WhatsAppTemplate.objects.create(
    project=spj,
    name='SPJ Follow-up',
    template_type='TEXT',
    category='followup',
    message_text='Hi {name}, this is a follow-up regarding your interest in SPJ Vedatam. Are you available for a site visit?',
    api_key='YOUR_AISENSY_API_KEY_HERE',
    campaign_name='spj_followup',
    order=2,
    is_active=True
)

# Template 3: Site Visit Reminder
WhatsAppTemplate.objects.create(
    project=spj,
    name='SPJ Site Visit',
    template_type='TEXT',
    category='reminder',
    message_text='Hi {name}, we would love to show you SPJ Vedatam. Book your site visit today!',
    api_key='YOUR_AISENSY_API_KEY_HERE',
    campaign_name='spj_sitevisit',
    order=3,
    is_active=True
)

print("✓ Created 3 WhatsApp templates for SPJ!")
print(f"Total templates: {spj.whatsapp_templates.count()}")
```

**IMPORTANT:** Replace `YOUR_AISENSY_API_KEY_HERE` with your actual AISensy API key!

---

## Where to Get AISensy API Key?

1. Login to AISensy dashboard
2. Go to Settings → API
3. Copy your API key
4. Replace in the script above

---

## Alternative: Create via Web Interface

1. Go to: `/projects/` (your projects list)
2. Click on **SPJ** project
3. Click **WhatsApp Templates** tab
4. Click **Add Template**
5. Fill in:
   - **Name:** SPJ Welcome
   - **Message:** Hi {name}, thank you for your interest!
   - **API Key:** Your AISensy key
   - **Campaign Name:** spj_welcome
   - **Category:** Welcome
6. Save
7. Repeat for more templates

---

## After Creating Templates

Refresh the bulk WhatsApp page:
`/projects/{project_id}/bulk-whatsapp/`

You should now see:
- **Total Leads: 448** ✅
- **With Phone: 447** ✅
- **Available Templates: 3** ✅
- Dropdown will show: SPJ Welcome, SPJ Follow-up, SPJ Site Visit

---

## For Gaur Project

If you also need templates for Gaur project:

```python
from leads.project_models import Project
from leads.whatsapp_models import WhatsAppTemplate

# Get Gaur project
gaur = Project.objects.filter(name__icontains='Gaur').first()

if gaur:
    WhatsAppTemplate.objects.create(
        project=gaur,
        name='Gaur Welcome',
        template_type='TEXT',
        category='welcome',
        message_text='Hi {name}, thank you for your interest in Gaur Yamuna City!',
        api_key='YOUR_AISENSY_API_KEY_HERE',
        campaign_name='gaur_welcome',
        order=1,
        is_active=True
    )
    print(f"✓ Created template for {gaur.name}")
else:
    print("Gaur project not found. Create it first!")
```

---

## Check All Projects

```python
from leads.project_models import Project

for project in Project.objects.all():
    templates = project.whatsapp_templates.count()
    leads = project.get_leads().count()
    print(f"{project.name}: {leads} leads, {templates} templates")
```

---

## Summary

**Problem:** No WhatsApp templates configured
**Solution:** Create templates using script above
**Result:** Dropdown will show available campaigns

**Next:** Get your AISensy API key and run the script!
