import requests
import sqlite3
import json
from flask import Flask, jsonify

app = Flask(__name__)

ACCESS_TOKEN = 'EAAgVjAbsIWoBPmzUD4hZBAOXBu1ZCVs3K4ART8wXpJGEs6iUijYIPWH3iDpC2McbFc8v0r6J17n0qAquuvesg9eAo1A4fUUDGpyOhWZBVjYVH4XIk5f2SBCPrVn8cyKEVCECOl3j5wZBYqGLBs9WZCrLblhdszL93e8IafZA591fXZCAZADrOZAP7g1ZAMdNDYJGc4bqotsiOoBLZCnBZAT32fxh4ZBMIGIAnIAasDDU2u6ZCfw5sZD'
PAGE_ID = '296508423701621'

def init_db():
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

def fetch_leads():
    url = f'https://graph.facebook.com/v23.0/{PAGE_ID}/leadgen_forms'
    params = {'access_token': ACCESS_TOKEN}
    
    forms_response = requests.get(url, params=params)
    forms = forms_response.json().get('data', [])
    
    conn = sqlite3.connect('leads.db')
    
    for form in forms:
        form_id = form['id']
        form_name = form.get('name', 'Unknown')
        
        leads_url = f'https://graph.facebook.com/v23.0/{form_id}/leads'
        leads_params = {
            'access_token': ACCESS_TOKEN,
            'fields': 'id,created_time,field_data'
        }
        
        leads_response = requests.get(leads_url, params=leads_params)
        leads = leads_response.json().get('data', [])
        
        for lead in leads:
            field_data = lead.get('field_data', [])
            email = next((f['values'][0] for f in field_data if f['name'] == 'email'), '')
            full_name = next((f['values'][0] for f in field_data if f['name'] == 'full_name'), '')
            phone = next((f['values'][0] for f in field_data if f['name'] == 'phone_number'), '')
            
            conn.execute('''INSERT OR REPLACE INTO leads 
                           (lead_id, created_time, email, full_name, phone_number, form_name)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (lead['id'], lead['created_time'], email, full_name, phone, form_name))
    
    conn.commit()
    conn.close()

@app.route('/leads')
def get_leads():
    conn = sqlite3.connect('leads.db')
    cursor = conn.execute('SELECT * FROM leads ORDER BY created_time DESC')
    leads = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(leads)

@app.route('/sync-leads', methods=['POST'])
def sync_leads():
    try:
        fetch_leads()
        return jsonify({'message': 'Leads synced successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print('Server running on http://localhost:5000')
    print('POST /sync-leads - Sync leads from Meta')
    print('GET /leads - View all leads')
    app.run(debug=True, port=5000)