# Fix SPJ Project - Link Leads

## Problem
Your SPJ project shows:
- **Total Leads: 0** 
- **Available Templates: 0**

But you have 388 leads with phone numbers in the database.

## Root Cause
The SPJ project doesn't have **form_keywords** configured, so it can't find its leads.

---

## Solution 1: Add Form Keywords (Quick Fix - 2 minutes)

### Step 1: Find Your Form Names

Run this in Django shell:

```bash
python manage.py shell
```

```python
from leads.models import Lead

# Get all unique form names
form_names = Lead.objects.values_list('form_name', flat=True).distinct()
for form in form_names:
    count = Lead.objects.filter(form_name=form).count()
    print(f"{form}: {count} leads")
```

### Step 2: Update SPJ Project

Find which form names belong to SPJ (look for "SPJ", "Saya", "Piazza", "Jaipur" etc.)

```python
from leads.project_models import Project

# Get SPJ project
spj = Project.objects.get(code='SPJ')  # or name__icontains='SPJ'

# Add form keywords (REPLACE WITH YOUR ACTUAL FORM NAMES)
spj.form_keywords = ['SPJ', 'Saya Piazza', 'Jaipur']
spj.save()

# Test it
print(f"SPJ now has {spj.get_leads().count()} leads")
```

---

## Solution 2: Use Form Mapping (Better - 5 minutes)

### Create Form Mappings

```python
from leads.project_models import Project
from leads.form_mapping_models import FormSourceMapping
from leads.models import Lead

# Get SPJ project
spj = Project.objects.get(code='SPJ')

# Get all form names that should belong to SPJ
# REPLACE 'SPJ' with your actual form name pattern
spj_forms = Lead.objects.filter(form_name__icontains='SPJ').values_list('form_name', flat=True).distinct()

# Create mappings
for form_name in spj_forms:
    FormSourceMapping.objects.get_or_create(
        form_name=form_name,
        project=spj,
        defaults={'is_active': True}
    )
    print(f"Mapped: {form_name}")

# Verify
print(f"\nSPJ now has {spj.get_leads().count()} leads")
```

---

## Solution 3: Web Interface (Easiest - 1 minute)

### Option A: Edit Project

1. Go to: `https://your-domain.com/projects/`
2. Click on **SPJ** project
3. Click **Edit Project**
4. In **Form Keywords** field, add keywords separated by commas:
   ```
   SPJ, Saya Piazza, Jaipur
   ```
5. Save

### Option B: Form Mapping Page

1. Go to: `https://your-domain.com/form-mappings/`
2. Click **Bulk Create Mapping**
3. Select **SPJ** project
4. Enter form name pattern: `SPJ`
5. Click **Create Mappings**

---

## Fix WhatsApp Templates (0 templates issue)

### Create a Template

```python
from leads.project_models import Project
from leads.whatsapp_models import WhatsAppTemplate

spj = Project.objects.get(code='SPJ')

# Create a welcome template
WhatsAppTemplate.objects.create(
    project=spj,
    name='SPJ Welcome Message',
    template_type='TEXT',
    category='welcome',
    message_text='Hi {name}, thank you for your interest in Saya Piazza Jaipur!',
    api_key='your_aisensy_api_key',
    campaign_name='spj_welcome',
    order=1,
    is_active=True
)

print("Template created!")
```

Or create via web interface:
1. Go to: `https://your-domain.com/projects/{project_id}/whatsapp-templates/`
2. Click **Add Template**
3. Fill in details
4. Save

---

## Quick Fix Script (Run This!)

```python
# Run in Django shell: python manage.py shell

from leads.project_models import Project
from leads.models import Lead
from leads.whatsapp_models import WhatsAppTemplate

# 1. Find SPJ project
try:
    spj = Project.objects.get(code='SPJ')
except:
    spj = Project.objects.filter(name__icontains='SPJ').first()

if not spj:
    print("❌ SPJ project not found!")
    print("Available projects:")
    for p in Project.objects.all():
        print(f"  - {p.name} ({p.code})")
else:
    print(f"✅ Found project: {spj.name}")
    
    # 2. Find form names with SPJ
    spj_forms = Lead.objects.filter(
        form_name__icontains='SPJ'
    ).values_list('form_name', flat=True).distinct()
    
    print(f"\n📋 Found {len(spj_forms)} form names with 'SPJ':")
    for form in spj_forms:
        count = Lead.objects.filter(form_name=form).count()
        print(f"  - {form}: {count} leads")
    
    # 3. Update project keywords
    if spj_forms:
        spj.form_keywords = list(spj_forms)
        spj.save()
        print(f"\n✅ Updated SPJ keywords")
    
    # 4. Verify leads
    total_leads = spj.get_leads().count()
    leads_with_phone = spj.get_leads().filter(
        phone_number__isnull=False
    ).exclude(phone_number='').count()
    
    print(f"\n📊 SPJ Project Stats:")
    print(f"  Total Leads: {total_leads}")
    print(f"  With Phone: {leads_with_phone}")
    
    # 5. Check templates
    templates = spj.whatsapp_templates.count()
    print(f"  Templates: {templates}")
    
    if templates == 0:
        print("\n⚠️ No templates found. Create one at:")
        print(f"  /projects/{spj.id}/whatsapp-templates/")
```

---

## Verify It Works

After running the fix:

1. Go to: `https://your-domain.com/projects/{project_id}/bulk-whatsapp/`
2. You should now see:
   - **Total Leads: 388** (or your actual count)
   - **With Phone: 388**
   - **Available Templates: 1+**

---

## Common Issues

### "No form names found with SPJ"

Your form names might use different keywords. Check all forms:

```python
from leads.models import Lead

# Show all form names
for form in Lead.objects.values_list('form_name', flat=True).distinct():
    print(form)
```

Look for patterns like:
- "Saya Piazza"
- "Jaipur"
- "SPJ"
- Or any other identifier

### "Still showing 0 leads"

Clear cache and restart:

```bash
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
sudo systemctl restart crm
```

---

## Summary

**Problem:** SPJ project not linked to leads
**Solution:** Add form_keywords or create FormSourceMapping
**Result:** Leads will appear, WhatsApp campaigns will work

**Next Steps:**
1. Run the Quick Fix Script above
2. Create WhatsApp templates
3. Test bulk WhatsApp sending
