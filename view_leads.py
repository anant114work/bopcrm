import sqlite3
import json

def view_leads_summary():
    conn = sqlite3.connect('leads.db')
    
    # Get total count
    cursor = conn.execute('SELECT COUNT(*) FROM leads')
    total = cursor.fetchone()[0]
    
    # Get leads by form
    cursor = conn.execute('SELECT form_name, COUNT(*) FROM leads GROUP BY form_name ORDER BY COUNT(*) DESC')
    forms = cursor.fetchall()
    
    # Get recent leads
    cursor = conn.execute('SELECT lead_id, full_name, email, form_name, created_time FROM leads ORDER BY created_time DESC LIMIT 10')
    recent = cursor.fetchall()
    
    conn.close()
    
    print(f"=== META LEADS CRM SUMMARY ===")
    print(f"Total Leads: {total}")
    print(f"\nLeads by Form:")
    for form_name, count in forms:
        print(f"  {count:2d} - {form_name}")
    
    print(f"\nRecent 10 Leads:")
    for lead in recent:
        name = lead[1] if lead[1] else "No Name"
        email = lead[2] if lead[2] else "No Email"
        form = lead[3][:30] + "..." if len(lead[3]) > 30 else lead[3]
        print(f"  {name} | {email} | {form}")

def export_leads_csv():
    conn = sqlite3.connect('leads.db')
    cursor = conn.execute('SELECT * FROM leads ORDER BY created_time DESC')
    leads = cursor.fetchall()
    conn.close()
    
    with open('leads_export.csv', 'w', encoding='utf-8') as f:
        f.write("ID,Lead_ID,Created_Time,Email,Full_Name,Phone,Form_Name\n")
        for lead in leads:
            f.write(f"{lead[0]},{lead[1]},{lead[2]},{lead[3]},{lead[4]},{lead[5]},{lead[6]}\n")
    
    print(f"Exported {len(leads)} leads to leads_export.csv")

if __name__ == "__main__":
    view_leads_summary()
    print("\nExporting to CSV...")
    export_leads_csv()