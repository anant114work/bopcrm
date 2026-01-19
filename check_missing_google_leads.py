#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

# Google Sheet leads data
google_sheet_leads = [
    {"name": "Anil Kumar", "phone": "7015837345", "email": "anilparbhuwala1@gmail.com", "date": "19/11/2025"},
    {"name": "Satya pramanik", "phone": "8130118019", "email": "satyapramaniksmb@gmail.com", "date": "19/11/2025"},
    {"name": "Chinedu onyekelu", "phone": "9863543954", "email": "chineduonyekelu0@gmail.com", "date": "19/11/2025"},
    {"name": "Praveen Kumar", "phone": "7042628066", "email": "pkhdfc0439@gmail.com", "date": "19/11/2025"},
    {"name": "Subhashu", "phone": "9810890895", "email": "", "date": "19/11/2025"},
    {"name": "Sanjana", "phone": "9029187544", "email": "sanjnavalmiki558@gmail.com", "date": "20/11/2025"},
    {"name": "Kanha", "phone": "9555516935", "email": "", "date": "20/11/2025"},
    {"name": "Kaif khan", "phone": "9235351936", "email": "", "date": "20/11/2025"},
    {"name": "Ajay Kumar Das", "phone": "7044145429", "email": "ajaykumardas18@gmail.com", "date": "20/11/2025"},
    {"name": "D. V. Mittal", "phone": "9911912299", "email": "", "date": "20/11/2025"},
    {"name": "Rakesh Chawla", "phone": "9999453225", "email": "realtychawla@gmail.com", "date": "20/11/2025"},
    {"name": "MD Hask", "phone": "7775065369", "email": "mdhask99@gmail.com", "date": "21/11/2025"},
    {"name": "Anil kumar Rawat", "phone": "9210881700", "email": "anilrawat1700@gmail.com", "date": "22/11/2025"},
    {"name": "Mukesh Chaudhary", "phone": "7838964509", "email": "mukesh4139@gmail.com", "date": "22/11/2025"},
    {"name": "Ashish Goyal", "phone": "9871032444", "email": "", "date": "23/11/2025"},
    {"name": "Ashish Kumar", "phone": "9871032444", "email": "", "date": "23/11/2025"},
    {"name": "Amit", "phone": "9911504543", "email": "", "date": "23/11/2025"},
    {"name": "DEVENDRA KUMAR", "phone": "9990725361", "email": "devenkumar0009@gmail.com", "date": "24/11/2025"},
    {"name": "Rahul Gupta", "phone": "8505969871", "email": "rahulyuvi001@gmail.com", "date": "24/11/2025"},
    {"name": "Mb", "phone": "9811189960", "email": "kiitmanishkiit@gmail.com", "date": "24/11/2025"},
    {"name": "Gaurav", "phone": "8882943206", "email": "reenusisodiya@gmail.com", "date": "25/11/2025"},
    {"name": "AMAR PRAKASH", "phone": "7037460170", "email": "amarprakash75@gmail.com", "date": "25/11/2025"},
    {"name": "arshad javed", "phone": "9910904222", "email": "arshadj8701@gmail.com", "date": "25/11/2025"},
    {"name": "Shyam Kumar Singh", "phone": "9212106862", "email": "IMISHYAM78@GMAIL.COM", "date": "25/11/2025"},
    {"name": "Seema singh", "phone": "8826229653", "email": "seemasingh5jan@gmail.com", "date": "26/11/2025"},
    {"name": "Shambhu Nautiyal", "phone": "9953256711", "email": "shambhu.nautiyal@gmail.com", "date": "26/11/2025"},
    {"name": "Saas", "phone": "8055225588", "email": "skmitt76@gmail.com", "date": "26/11/2025"},
    {"name": "P K Verma", "phone": "9575304113", "email": "parimalkantverma@gmail.com", "date": "27/11/2025"},
    {"name": "Radha", "phone": "8860277844", "email": "shrdeeyp@gmail.com", "date": "27/11/2025"},
    {"name": "test", "phone": "9876543210", "email": "test@gmail.com", "date": "27/11/2025"},
    {"name": "Rajan Taluja", "phone": "8130400017", "email": "rajantaluja@gmail.com", "date": "27/11/2025"},
    {"name": "Shyam Kumar Singh", "phone": "9212106867", "email": "IMISHYAM78@GMAIL.COM", "date": "28/11/2025"},
    {"name": "Khanki", "phone": "8159054910", "email": "khanki_intl88@gmail.com", "date": "28/11/2025"},
    {"name": "Ramesh", "phone": "9899284849", "email": "rcsethi52@gmail.com", "date": "28/11/2025"},
    {"name": "Vineet Sharma", "phone": "8588887600", "email": "vsharma.kba@gmail.com", "date": "29/11/2025"},
    {"name": "ABC gupta", "phone": "9643158442", "email": "abcgupta@gmail.com", "date": "29/11/2025"},
    {"name": "sk singhi", "phone": "9810857478", "email": "surendrasinghi1958@gmail.com", "date": "30/11/2025"},
    {"name": "Sudip Mukhopadhyay", "phone": "9910202616", "email": "sudip1geo@yahoo.com", "date": "01/12/2025"},
    {"name": "Anil", "phone": "9990279946", "email": "pugalia.anil@gmail.com", "date": "01/12/2025"},
    {"name": "Shreya", "phone": "7340858013", "email": "prakashshreya0904@gmail.com", "date": "01/12/2025"},
    {"name": "Arun Chhabra", "phone": "9650997257", "email": "varun41777@gmail.com", "date": "02/12/2025"},
    {"name": "Abhishek Mishra", "phone": "9015123888", "email": "abhishekm300@gmail.com", "date": "02/12/2025"},
    {"name": "Farman Saifi", "phone": "9027392542", "email": "farmansaifivlogs@gmail.com", "date": "02/12/2025"},
    {"name": "Santosh Kumar Thakur", "phone": "8929570323", "email": "santoshjithakur1985@gmail.com", "date": "02/12/2025"},
    {"name": "Nitish", "phone": "7906704502", "email": "nitish.vashishth@icloud.com", "date": "03/12/2025"},
    {"name": "Arun", "phone": "9650997257", "email": "varun41777@gmail.com", "date": "03/12/2025"},
    {"name": "Karamveer awana", "phone": "9958434142", "email": "kvawana570@gmail.com", "date": "04/12/2025"},
    {"name": "Puneet Khanna", "phone": "9312890289", "email": "dnkshalini@gmail.com", "date": "04/12/2025"},
    {"name": "Harshit Surana", "phone": "7678186306", "email": "hrshtsurana10@gmail.com", "date": "04/12/2025"},
    {"name": "Saurabh", "phone": "8447738612", "email": "srbhsethi1990@gmail.com", "date": "05/12/2025"},
    {"name": "Ayush Tiwari", "phone": "8340477897", "email": "ayushrajgaurmukh12345@gmail.com", "date": "05/12/2025"},
    {"name": "C K Joseph", "phone": "9811900711", "email": "ckjoseph59@gmail.com", "date": "05/12/2025"},
    {"name": "Anand lal", "phone": "9212555818", "email": "lalandsons7@gmail.com", "date": "05/12/2025"},
    {"name": "Ashok Gupta", "phone": "8851484031", "email": "akgupta0505@gmail.com", "date": "06/12/2025"},
    {"name": "Umesh Gupta", "phone": "9602713139", "email": "umeshg2011@gmail.com", "date": "06/12/2025"},
    {"name": "Jay singh", "phone": "9560054540", "email": "vijaygglobal@gmail.com", "date": "06/12/2025"},
    {"name": "vikas", "phone": "9873733868", "email": "mac.timar@gmail.com", "date": "06/12/2025"},
    {"name": "Sachin dua", "phone": "9313531451", "email": "duasachin198578@gmail.com", "date": "06/12/2025"},
    {"name": "Kasturi Lal Bhatia", "phone": "8447094562", "email": "enterneelam@gmail.com", "date": "06/12/2025"},
    {"name": "Ankit KUMAR", "phone": "8419994584", "email": "raghavankit47@gmail.com", "date": "06/12/2025"},
    {"name": "Pankaj kumar", "phone": "8337078107", "email": "pksinha.alb@gmail.com", "date": "06/12/2025"},
    {"name": "Praveen", "phone": "9999817982", "email": "praveenarunajain@gmail.com", "date": "07/12/2025"},
    {"name": "Anand", "phone": "9810098100", "email": "anand@gmail.com", "date": "07/12/2025"},
    {"name": "Harsh Juneja", "phone": "8383057087", "email": "harsh1028@gmail.com", "date": "07/12/2025"},
    {"name": "abcd jain", "phone": "9811110000", "email": "abc@gmail.com", "date": "07/12/2025"},
    {"name": "OM PRAKASH MISHRA", "phone": "9313003650", "email": "mishraop62@gmail.com", "date": "07/12/2025"},
    {"name": "Sachin Chauhan", "phone": "8130538451", "email": "sachinamutech@gmail.com", "date": "07/12/2025"},
    {"name": "Vinod", "phone": "9540486939", "email": "singhvinod915@gmail.com", "date": "08/12/2025"},
    {"name": "Vinod", "phone": "9540486936", "email": "singhvinod915@gmail.com", "date": "08/12/2025"},
    {"name": "Saurabh chauhan", "phone": "9313182779", "email": "Saurabhc0007@gmail.com", "date": "08/12/2025"},
    {"name": "Ankur Gupta", "phone": "9650169018", "email": "ankur.jiitqn@gmail.com", "date": "08/12/2025"},
    {"name": "Ankur Gupta", "phone": "9643825852", "email": "ankur.jiitn@gmail.com", "date": "08/12/2025"},
    {"name": "Chirag Bansal", "phone": "9999228828", "email": "chiragbansal@greyradius.com", "date": "09/12/2025"},
    {"name": "Hemant gogari", "phone": "9403648123", "email": "hemant.gogari@gmail.com", "date": "09/12/2025"},
    {"name": "Animesh Sinha", "phone": "9999464305", "email": "sinha.animesh@gmail.com", "date": "09/12/2025"},
    {"name": "Raghvendra Kumar yadav", "phone": "8999633887", "email": "", "date": "09/12/2025"},
    {"name": "Kritika Tewani", "phone": "9818725777", "email": "anukriti.bindal@gmail.com", "date": "09/12/2025"},
    {"name": "A K Pandey", "phone": "9899186170", "email": "ashwini.pandey@live.in", "date": "09/12/2025"},
    {"name": "Ajay Gambhir", "phone": "9311557085", "email": "drajaygambhir@gmail.com", "date": "09/12/2025"},
    {"name": "Amit Tiwary", "phone": "9015190562", "email": "Amittiwaryca@gmail.com", "date": "10/12/2025"},
    {"name": "Sksinha", "phone": "9818612928", "email": "SKSinhadelhi@yahoo.com", "date": "10/12/2025"},
    {"name": "Uday Shankar sahay", "phone": "9973760787", "email": "", "date": "10/12/2025"},
    {"name": "Anil", "phone": "8510098308", "email": "anilbhati2308@gmail.com", "date": "10/12/2025"},
    {"name": "Hemendra", "phone": "9818648647", "email": "", "date": "10/12/2025"},
    {"name": "Keshav chand Rustagi", "phone": "9810095590", "email": "keshav.rustagi@yahoo.com", "date": "10/12/2025"},
    {"name": "Rohit", "phone": "9911414353", "email": "indusharma@123g.mai", "date": "10/12/2025"},
    {"name": "Kheem singh", "phone": "9891341347", "email": "singhkheem17@gmail.com", "date": "11/12/2025"},
    {"name": "Vikas Malhotra", "phone": "9212109002", "email": "vksmal@gmail.com", "date": "11/12/2025"},
    {"name": "Anirudh", "phone": "9811868611", "email": "", "date": "11/12/2025"},
    {"name": "Dhiresh Malik", "phone": "9999710075", "email": "dhiresh25@gmail.com", "date": "11/12/2025"},
    {"name": "Anju Kaushik", "phone": "9650189757", "email": "anjukaushik79@gmail.com", "date": "11/12/2025"},
    {"name": "Amit Kumar", "phone": "9716881663", "email": "amitenjoyable@gmail.com", "date": "11/12/2025"},
    {"name": "Satish", "phone": "9910487432", "email": "edqacskp@gmail.com", "date": "11/12/2025"},
    {"name": "Roseline Wilfred", "phone": "9999715025", "email": "roselinewilfred1954@gmail.com", "date": "12/12/2025"},
    {"name": "Sarjeet Singh", "phone": "9810805648", "email": "sarjeet01@yahoo.co.in", "date": "12/12/2025"},
    {"name": "Subhash", "phone": "9650296565", "email": "SUBHASHCHANDRA0512@GMAIL.COM", "date": "12/12/2025"},
    {"name": "ruchipanna tiwari", "phone": "7058792708", "email": "pannachauhan53@gmail.com", "date": "12/12/2025"},
    {"name": "Ritesh Kothiyal", "phone": "9910266552", "email": "test@gmail.com", "date": "12/12/2025"},
    {"name": "Vikas", "phone": "9650100596", "email": "kevinn.shankar@gmail.com", "date": "12/12/2025"},
]

def normalize_phone(phone):
    """Normalize phone number for comparison"""
    if not phone or phone == "#ERROR!":
        return ""
    # Remove spaces, dashes, and special characters
    normalized = str(phone).replace(' ', '').replace('-', '').replace('+', '').replace('(', '').replace(')', '')
    # Remove country code if present
    if normalized.startswith('91') and len(normalized) == 12:
        normalized = normalized[2:]
    return normalized

def check_missing_leads():
    print("Checking Google Sheet leads against CRM database...")
    print("=" * 80)
    
    missing_leads = []
    found_leads = []
    
    for gs_lead in google_sheet_leads:
        phone = normalize_phone(gs_lead['phone'])
        if not phone:
            continue
            
        # Check multiple phone formats
        phone_variants = [
            phone,
            f"+91{phone}",
            f"91{phone}",
            gs_lead['phone']  # Original format
        ]
        
        # Search in CRM
        crm_lead = Lead.objects.filter(phone_number__in=phone_variants).first()
        
        if crm_lead:
            found_leads.append({
                'gs_name': gs_lead['name'],
                'gs_phone': gs_lead['phone'],
                'crm_name': crm_lead.full_name,
                'crm_phone': crm_lead.phone_number,
                'crm_source': crm_lead.source,
                'date': gs_lead['date']
            })
        else:
            missing_leads.append(gs_lead)
    
    print(f"SUMMARY:")
    print(f"   Total Google Sheet leads: {len(google_sheet_leads)}")
    print(f"   Found in CRM: {len(found_leads)}")
    print(f"   Missing from CRM: {len(missing_leads)}")
    print("=" * 80)
    
    if missing_leads:
        print(f"\nMISSING LEADS ({len(missing_leads)}):")
        print("-" * 60)
        for lead in missing_leads:
            print(f"   {lead['name']} | {lead['phone']} | {lead['email']} | {lead['date']}")
    
    if found_leads:
        print(f"\nFOUND LEADS ({len(found_leads)}):")
        print("-" * 60)
        for lead in found_leads[:10]:  # Show first 10
            print(f"   {lead['gs_name']} | {lead['gs_phone']} | {lead['crm_source']}")
        if len(found_leads) > 10:
            print(f"   ... and {len(found_leads) - 10} more")
    
    print("\n" + "=" * 80)
    
    # Check why leads might be missing
    print("\nPOSSIBLE REASONS FOR MISSING LEADS:")
    print("1. Auto-sync not running or failed")
    print("2. Phone number format mismatch")
    print("3. Leads created after last sync")
    print("4. Google Sheets webhook not configured")
    print("5. Duplicate prevention blocking valid leads")

if __name__ == "__main__":
    check_missing_leads()