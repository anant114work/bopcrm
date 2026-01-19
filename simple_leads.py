import requests
import json
import sqlite3
from datetime import datetime

# Configuration
ACCESS_TOKEN = 'EAAgVjAbsIWoBPmzUD4hZBAOXBu1ZCVs3K4ART8wXpJGEs6iUijYIPWH3iDpC2McbFc8v0r6J17n0qAquuvesg9eAo1A4fUUDGpyOhWZBVjYVH4XIk5f2SBCPrVn8cyKEVCECOl3j5wZBYqGLBs9WZCrLblhdszL93e8IafZA591fXZCAZADrOZAP7g1ZAMdNDYJGc4bqotsiOoBLZCnBZAT32fxh4ZBMIGIAnIAasDDU2u6ZCfw5sZD'
PAGE_ID = '296508423701621'

def init_database():
    conn = sqlite3.connect('leads.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id TEXT UNIQUE,
        created_time TEXT,
        email TEXT,
        full_name TEXT,
        phone_number TEXT,
        form_name TEXT
    )''')
    conn.commit()
    conn.close()

def fetch_and_store_leads():
    # Get lead forms
    forms_url = f'https://graph.facebook.com/v23.0/{PAGE_ID}/leadgen_forms'
    forms_params = {'access_token': ACCESS_TOKEN}
    
    forms_response = requests.get(forms_url, params=forms_params)
    forms_data = forms_response.json()
    
    if 'error' in forms_data:
        print(f"Error fetching forms: {forms_data['error']['message']}")
        return
    
    forms = forms_data.get('data', [])
    print(f"Found {len(forms)} lead forms")
    
    conn = sqlite3.connect('leads.db')
    total_leads = 0
    
    for form in forms:
        form_id = form['id']
        form_name = form.get('name', 'Unknown Form')
        
        # Get leads for this form
        leads_url = f'https://graph.facebook.com/v23.0/{form_id}/leads'
        leads_params = {
            'access_token': ACCESS_TOKEN,
            'fields': 'id,created_time,field_data'
        }
        
        leads_response = requests.get(leads_url, params=leads_params)
        leads_data = leads_response.json()
        
        if 'error' in leads_data:
            print(f"Error fetching leads for form {form_name}: {leads_data['error']['message']}")
            continue
        
        leads = leads_data.get('data', [])
        print(f"Form '{form_name}': {len(leads)} leads")
        
        for lead in leads:
            field_data = lead.get('field_data', [])
            
            # Extract common fields
            email = ''
            full_name = ''
            phone_number = ''
            
            for field in field_data:
                if field['name'] == 'email':
                    email = field['values'][0] if field['values'] else ''
                elif field['name'] == 'full_name':
                    full_name = field['values'][0] if field['values'] else ''
                elif field['name'] == 'phone_number':
                    phone_number = field['values'][0] if field['values'] else ''
            
            # Store in database
            try:
                conn.execute('''INSERT OR REPLACE INTO leads 
                               (lead_id, created_time, email, full_name, phone_number, form_name)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (lead['id'], lead['created_time'], email, full_name, phone_number, form_name))
                total_leads += 1
            except Exception as e:
                print(f"Error storing lead {lead['id']}: {e}")
    
    conn.commit()
    conn.close()
    print(f"Successfully stored {total_leads} leads")

def view_leads():
    conn = sqlite3.connect('leads.db')
    cursor = conn.execute('SELECT * FROM leads ORDER BY created_time DESC')
    leads = cursor.fetchall()
    conn.close()
    
    if not leads:
        print("No leads found in database")
        return
    
    print(f"\n=== {len(leads)} LEADS IN CRM ===")
    for lead in leads:
        print(f"ID: {lead[1]}")
        print(f"Name: {lead[4]}")
        print(f"Email: {lead[3]}")
        print(f"Phone: {lead[5]}")
        print(f"Form: {lead[6]}")
        print(f"Date: {lead[2]}")
        print("-" * 40)

if __name__ == "__main__":
    print("Meta Leads CRM - Simple Version")
    print("1. Initializing database...")
    init_database()
    
    print("2. Fetching leads from Meta...")
    fetch_and_store_leads()
    
    print("3. Displaying stored leads...")
    view_leads()