#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime
from django.utils import timezone
import pytz

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import Lead

# Your Google Sheets data with correct dates
google_sheets_data = [
    {'date': '19/11/2025 17:11:25', 'name': 'Anil Kumar', 'phone': '7015837345', 'email': 'anilparbhuwala1@gmail.com'},
    {'date': '19/11/2025 17:13:36', 'name': 'Satya pramanik', 'phone': '8130118019', 'email': 'satyapramaniksmb@gmail.com'},
    {'date': '19/11/2025 17:14:19', 'name': 'Chinedu onyekelu', 'phone': '9863543954', 'email': 'chineduonyekelu0@gmail.com'},
    {'date': '19/11/2025 17:16:22', 'name': 'Praveen Kumar', 'phone': '7042628066', 'email': 'pkhdfc0439@gmail.com'},
    {'date': '19/11/2025 17:22:31', 'name': 'Subhashu', 'phone': '9810890895', 'email': ''},
    {'date': '20/11/2025 07:01:31', 'name': 'Sanjana', 'phone': '9029187544', 'email': 'sanjnavalmiki558@gmail.com'},
    {'date': '20/11/2025 08:32:47', 'name': 'Kanha', 'phone': '9555516935', 'email': ''},
    {'date': '20/11/2025 10:15:43', 'name': 'Kaif khan', 'phone': '9235351936', 'email': ''},
    {'date': '20/11/2025 15:56:08', 'name': 'Ajay Kumar Das', 'phone': '7044145429', 'email': 'ajaykumardas18@gmail.com'},
    {'date': '20/11/2025 16:06:04', 'name': 'D. V. Mittal', 'phone': '9911912299', 'email': ''},
    {'date': '20/11/2025 22:13:38', 'name': 'Rakesh Chawla', 'phone': '9999453225', 'email': 'realtychawla@gmail.com'},
    {'date': '21/11/2025 16:40:30', 'name': 'MD Hask', 'phone': '7775065369', 'email': 'mdhask99@gmail.com'},
    {'date': '22/11/2025 13:38:43', 'name': 'Anil kumar Rawat', 'phone': '9210881700', 'email': 'anilrawat1700@gmail.com'},
    {'date': '22/11/2025 15:04:16', 'name': 'Mukesh Chaudhary', 'phone': '7838964509', 'email': 'mukesh4139@gmail.com'},
    {'date': '23/11/2025 12:56:38', 'name': 'Ashish Goyal', 'phone': '9871032444', 'email': ''},
    {'date': '23/11/2025 12:56:43', 'name': 'Ashish Kumar', 'phone': '9871032444', 'email': ''},
    {'date': '23/11/2025 12:58:48', 'name': 'Amit', 'phone': '9911504543', 'email': ''},
    {'date': '23/11/2025 14:09:12', 'name': 'MD Hask', 'phone': '7775065369', 'email': 'mdhask99@gmail.com'},
    {'date': '24/11/2025 11:09:59', 'name': 'DEVENDRA KUMAR', 'phone': '9990725361', 'email': 'devenkumar0009@gmail.com'},
    {'date': '24/11/2025 11:53:57', 'name': 'Rahul Gupta', 'phone': '8505969871', 'email': 'rahulyuvi001@gmail.com'},
    {'date': '24/11/2025 11:54:48', 'name': 'Rahul Gupta', 'phone': '8505969871', 'email': 'rahulyuvi001@gmail.com'},
    {'date': '24/11/2025 12:08:00', 'name': 'Mb', 'phone': '9811189960', 'email': 'kiitmanishkiit@gmail.com'},
    {'date': '25/11/2025 07:57:02', 'name': 'Gaurav', 'phone': '8882943206', 'email': 'reenusisodiya@gmail.com'},
    {'date': '25/11/2025 10:58:56', 'name': 'AMAR PRAKASH', 'phone': '7037460170', 'email': 'amarprakash75@gmail.com'},
    {'date': '25/11/2025 11:24:27', 'name': 'arshad javed', 'phone': '9910904222', 'email': 'arshadj8701@gmail.com'},
    {'date': '25/11/2025 16:36:33', 'name': 'Shyam Kumar Singh', 'phone': '9212106862', 'email': 'IMISHYAM78@GMAIL.COM'},
    {'date': '26/11/2025 08:46:43', 'name': 'Seema singh', 'phone': '8826229653', 'email': 'seemasingh5jan@gmail.com'},
    {'date': '26/11/2025 17:22:44', 'name': 'Shambhu Nautiyal', 'phone': '9953256711', 'email': 'shambhu.nautiyal@gmail.com'},
    {'date': '26/11/2025 19:32:10', 'name': 'Saas', 'phone': '8055225588', 'email': 'skmitt76@gmail.com'},
    {'date': '27/11/2025 08:48:05', 'name': 'P K Verma', 'phone': '9575304113', 'email': 'parimalkantverma@gmail.com'},
    {'date': '27/11/2025 15:30:45', 'name': 'Radha', 'phone': '8860277844', 'email': 'shrdeeyp@gmail.com'},
    {'date': '27/11/2025 15:32:28', 'name': 'Radha', 'phone': '8860277844', 'email': 'shrdeeyp@gmail.com'},
    {'date': '27/11/2025 17:48:48', 'name': 'test', 'phone': '9876543210', 'email': 'test@gmail.com'},
    {'date': '27/11/2025 19:39:13', 'name': 'Rajan Taluja', 'phone': '8130400017', 'email': 'rajantaluja@gmail.com'},
    {'date': '28/11/2025 09:53:54', 'name': 'Shyam Kumar Singh', 'phone': '9212106867', 'email': 'IMISHYAM78@GMAIL.COM'},
    {'date': '28/11/2025 16:13:16', 'name': 'Khanki', 'phone': '8159054910', 'email': 'khanki_intl88@gmail.com'},
    {'date': '28/11/2025 20:24:36', 'name': 'Ramesh', 'phone': '9899284849', 'email': 'rcsethi52@gmail.com'},
    {'date': '29/11/2025 12:09:10', 'name': 'Vineet Sharma', 'phone': '8588887600', 'email': 'vsharma.kba@gmail.com'},
    {'date': '29/11/2025 12:38:59', 'name': 'ABC gupta', 'phone': '9643158442', 'email': 'abcgupta@gmail.com'},
    {'date': '30/11/2025 10:25:42', 'name': 'sk singhi', 'phone': '9810857478', 'email': 'surendrasinghi1958@gmail.com'},
    {'date': '01/12/2025 08:04:43', 'name': 'Sudip Mukhopadhyay', 'phone': '9910202616', 'email': 'sudip1geo@yahoo.com'},
    {'date': '01/12/2025 08:08:27', 'name': 'Anil', 'phone': '9990279946', 'email': 'pugalia.anil@gmail.com'},
    {'date': '01/12/2025 13:43:00', 'name': 'Shreya', 'phone': '7340858013', 'email': 'prakashshreya0904@gmail.com'},
    {'date': '02/12/2025 09:03:20', 'name': 'Arun Chhabra', 'phone': '9650997257', 'email': 'varun41777@gmail.com'},
    {'date': '02/12/2025 09:16:38', 'name': 'Arun Chhabra', 'phone': '9650997257', 'email': 'varun41777@gmail.com'},
    {'date': '02/12/2025 10:08:42', 'name': 'Abhishek Mishra', 'phone': '9015123888', 'email': 'abhishekm300@gmail.com'},
    {'date': '02/12/2025 13:56:40', 'name': 'Farman Saifi', 'phone': '9027392542', 'email': 'farmansaifivlogs@gmail.com'},
    {'date': '02/12/2025 15:32:20', 'name': 'Santosh Kumar Thakur', 'phone': '8929570323', 'email': 'santoshjithakur1985@gmail.com'},
    {'date': '03/12/2025 10:15:22', 'name': 'Nitish', 'phone': '7906704502', 'email': 'nitish.vashishth@icloud.com'},
    {'date': '03/12/2025 19:32:18', 'name': 'Arun', 'phone': '9650997257', 'email': 'varun41777@gmail.com'},
    {'date': '04/12/2025 11:23:05', 'name': 'Karamveer awana', 'phone': '9958434142', 'email': 'kvawana570@gmail.com'},
    {'date': '04/12/2025 14:13:28', 'name': 'Puneet Khanna', 'phone': '9312890289', 'email': 'dnkshalini@gmail.com'},
    {'date': '04/12/2025 14:20:38', 'name': 'Puneet Khanna', 'phone': '9312890289', 'email': 'dnkshalini@gmail.com'},
    {'date': '04/12/2025 16:47:07', 'name': 'Harshit Surana', 'phone': '7678186306', 'email': 'hrshtsurana10@gmail.com'},
    {'date': '05/12/2025 15:14:34', 'name': 'Saurabh', 'phone': '8447738612', 'email': 'srbhsethi1990@gmail.com'},
    {'date': '05/12/2025 15:49:24', 'name': 'Ayush Tiwari', 'phone': '8340477897', 'email': 'ayushrajgaurmukh12345@gmail.com'},
    {'date': '05/12/2025 18:01:48', 'name': 'C K Joseph', 'phone': '9811900711', 'email': 'ckjoseph59@gmail.com'},
    {'date': '05/12/2025 18:04:02', 'name': 'C K Joseph', 'phone': '9811900711', 'email': 'ckjoseph59@gmail.com'},
    {'date': '05/12/2025 18:08:11', 'name': 'C K Joseph', 'phone': '9811900711', 'email': 'ckjoseph59@gmail.com'},
    {'date': '05/12/2025 19:15:54', 'name': 'Anand lal', 'phone': '9212555818', 'email': 'lalandsons7@gmail.com'},
    {'date': '05/12/2025 19:17:15', 'name': 'Anand lal', 'phone': '9212555818', 'email': 'lalandsons7@gmail.com'},
    {'date': '06/12/2025 08:13:12', 'name': 'Ashok Gupta', 'phone': '8851484031', 'email': 'akgupta0505@gmail.com'},
    {'date': '06/12/2025 08:33:44', 'name': 'Umesh Gupta', 'phone': '9602713139', 'email': 'umeshg2011@gmail.com'},
    {'date': '06/12/2025 10:23:06', 'name': 'Jay singh', 'phone': '9560054540', 'email': 'vijaygglobal@gmail.com'},
    {'date': '06/12/2025 11:12:51', 'name': 'vikas', 'phone': '9873733868', 'email': 'mac.timar@gmail.com'},
    {'date': '06/12/2025 19:50:33', 'name': 'Sachin dua', 'phone': '9313531451', 'email': 'duasachin198578@gmail.com'},
    {'date': '06/12/2025 20:03:54', 'name': 'Kasturi Lal Bhatia', 'phone': '8447094562', 'email': 'enterneelam@gmail.com'},
    {'date': '06/12/2025 20:46:18', 'name': 'Ankit KUMAR', 'phone': '8419994584', 'email': 'raghavankit47@gmail.com'},
    {'date': '06/12/2025 20:49:03', 'name': 'Ankit KUMAR', 'phone': '8419994584', 'email': 'raghavankit47@gmail.com'},
    {'date': '06/12/2025 21:48:46', 'name': 'Pankaj kumar', 'phone': '8337078107', 'email': 'pksinha.alb@gmail.com'},
    {'date': '07/12/2025 10:57:21', 'name': 'Nikku', 'phone': '', 'email': ''},
    {'date': '07/12/2025 12:00:09', 'name': 'Praveen', 'phone': '9999817982', 'email': 'praveenarunajain@gmail.com'},
    {'date': '07/12/2025 15:15:09', 'name': 'Anand', 'phone': '9810098100', 'email': 'anand@gmail.com'},
    {'date': '07/12/2025 17:46:35', 'name': 'Harsh Juneja', 'phone': '8383057087', 'email': 'harsh1028@gmail.com'},
    {'date': '07/12/2025 19:47:08', 'name': 'abcd jain', 'phone': '9811110000', 'email': 'abc@gmail.com'},
    {'date': '07/12/2025 20:46:29', 'name': 'OM PRAKASH MISHRA', 'phone': '9313003650', 'email': 'mishraop62@gmail.com'},
    {'date': '07/12/2025 22:24:00', 'name': 'Sachin Chauhan', 'phone': '8130538451', 'email': 'sachinamutech@gmail.com'},
    {'date': '08/12/2025 11:49:00', 'name': 'Vinod', 'phone': '9540486939', 'email': 'singhvinod915@gmail.com'},
    {'date': '08/12/2025 11:50:54', 'name': 'Vinod', 'phone': '9540486936', 'email': 'singhvinod915@gmail.com'},
    {'date': '08/12/2025 12:12:09', 'name': 'test', 'phone': '9876543210', 'email': 'test@gmail.com'},
    {'date': '08/12/2025 15:17:59', 'name': 'Saurabh chauhan', 'phone': '9313182779', 'email': 'Saurabhc0007@gmail.com'},
    {'date': '08/12/2025 17:36:29', 'name': 'Ankur Gupta', 'phone': '9650169018', 'email': 'ankur.jiitqn@gmail.com'},
    {'date': '08/12/2025 17:39:48', 'name': 'Ankur Gupta', 'phone': '9643825852', 'email': 'ankur.jiitn@gmail.com'},
    {'date': '09/12/2025 07:53:45', 'name': 'Chirag Bansal', 'phone': '9999228828', 'email': 'chiragbansal@greyradius.com'},
    {'date': '09/12/2025 10:04:04', 'name': 'Hemant gogari', 'phone': '9403648123', 'email': 'hemant.gogari@gmail.com'},
    {'date': '09/12/2025 15:03:15', 'name': 'Animesh Sinha', 'phone': '9999464305', 'email': 'sinha.animesh@gmail.com'},
    {'date': '09/12/2025 16:21:01', 'name': 'Raghvendra Kumar yadav', 'phone': '8999633887', 'email': ''},
    {'date': '09/12/2025 17:21:28', 'name': 'Kritika Tewani', 'phone': '9818725777', 'email': 'anukriti.bindal@gmail.com'},
    {'date': '09/12/2025 17:41:49', 'name': 'Rajender Singh', 'phone': '', 'email': 'rajendersro@gmail.com'},
    {'date': '09/12/2025 19:51:41', 'name': 'A K Pandey', 'phone': '9899186170', 'email': 'ashwini.pandey@live.in'},
    {'date': '09/12/2025 22:11:12', 'name': 'Ajay Gambhir', 'phone': '9311557085', 'email': 'drajaygambhir@gmail.com'},
    {'date': '10/12/2025 10:59:45', 'name': 'Amit Tiwary', 'phone': '9015190562', 'email': 'Amittiwaryca@gmail.com'},
    {'date': '10/12/2025 11:42:47', 'name': 'Sksinha', 'phone': '9818612928', 'email': 'SKSinhadelhi@yahoo.com'},
    {'date': '10/12/2025 12:22:05', 'name': 'Uday Shankar sahay', 'phone': '9973760787', 'email': ''},
    {'date': '10/12/2025 15:36:03', 'name': 'Anil', 'phone': '8510098308', 'email': 'anilbhati2308@gmail.com'},
    {'date': '10/12/2025 16:34:13', 'name': 'Hemendra', 'phone': '9818648647', 'email': ''},
    {'date': '10/12/2025 17:37:10', 'name': 'Keshav chand Rustagi', 'phone': '9810095590', 'email': 'keshav.rustagi@yahoo.com'},
    {'date': '10/12/2025 18:15:31', 'name': 'test', 'phone': '9876543210', 'email': 'test@gmail.com'},
    {'date': '10/12/2025 20:37:06', 'name': 'Rohit', 'phone': '9911414353', 'email': 'indusharma@123g.mai'},
    {'date': '10/12/2025 20:38:02', 'name': 'Rohit', 'phone': '9911414353', 'email': 'indusharma@123g.mai'},
    {'date': '11/12/2025 08:31:15', 'name': 'Kheem singh', 'phone': '9891341347', 'email': 'singhkheem17@gmail.com'},
    {'date': '11/12/2025 10:53:44', 'name': 'Vikas Malhotra', 'phone': '9212109002', 'email': 'vksmal@gmail.com'},
    {'date': '11/12/2025 11:06:02', 'name': 'Anirudh', 'phone': '9811868611', 'email': ''},
    {'date': '11/12/2025 11:25:09', 'name': 'Dhiresh Malik', 'phone': '9999710075', 'email': 'dhiresh25@gmail.com'},
    {'date': '11/12/2025 15:25:13', 'name': 'Anju Kaushik', 'phone': '9650189757', 'email': 'anjukaushik79@gmail.com'},
    {'date': '11/12/2025 15:25:53', 'name': 'Anju Kaushik', 'phone': '9650189757', 'email': 'anjukaushik79@gmail.com'},
    {'date': '11/12/2025 16:21:41', 'name': 'Amit Kumar', 'phone': '9716881663', 'email': 'amitenjoyable@gmail.com'},
    {'date': '11/12/2025 16:41:30', 'name': 'Satish', 'phone': '9910487432', 'email': 'edqacskp@gmail.com'},
    {'date': '12/12/2025 10:02:40', 'name': 'Roseline Wilfred', 'phone': '9999715025', 'email': 'roselinewilfred1954@gmail.com'},
    {'date': '12/12/2025 10:55:12', 'name': 'Sarjeet Singh', 'phone': '9810805648', 'email': 'sarjeet01@yahoo.co.in'},
    {'date': '12/12/2025 11:18:36', 'name': 'Subhash', 'phone': '9650296565', 'email': 'SUBHASHCHANDRA0512@GMAIL.COM'},
    {'date': '12/12/2025 11:32:03', 'name': 'ruchipanna tiwari', 'phone': '7058792708', 'email': 'pannachauhan53@gmail.com'},
]

def parse_date(date_str):
    """Parse date string in DD/MM/YYYY HH:MM:SS format"""
    try:
        # Parse the date string
        dt = datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
        # Convert to timezone-aware datetime (assuming IST)
        ist = pytz.timezone('Asia/Kolkata')
        dt_ist = ist.localize(dt)
        return dt_ist
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
        return None

def normalize_phone(phone):
    """Normalize phone number for matching"""
    if not phone:
        return []
    
    normalized = phone.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
    variants = [
        phone,
        normalized,
        f"+91{normalized}" if len(normalized) == 10 else f"+{normalized}",
        f"91{normalized}" if len(normalized) == 10 else normalized
    ]
    return list(set(variants))

def fix_google_sheets_dates():
    """Fix the dates for Google Sheets leads"""
    print("Starting to fix Google Sheets lead dates...")
    
    updated_count = 0
    not_found_count = 0
    
    for data in google_sheets_data:
        name = data['name']
        phone = data['phone']
        email = data['email']
        date_str = data['date']
        
        if not phone:  # Skip entries without phone numbers
            continue
            
        # Parse the correct date
        correct_date = parse_date(date_str)
        if not correct_date:
            continue
        
        # Find matching lead by phone number
        phone_variants = normalize_phone(phone)
        lead = Lead.objects.filter(
            phone_number__in=phone_variants,
            source='Google Sheets'
        ).first()
        
        if lead:
            # Update the created_time with correct date
            lead.created_time = correct_date
            
            # Also update extra_fields to store original timestamp
            if not lead.extra_fields:
                lead.extra_fields = {}
            lead.extra_fields['original_timestamp'] = date_str
            lead.extra_fields['date_fixed'] = True
            
            lead.save()
            updated_count += 1
            print(f"Updated {name} ({phone}) - Date: {correct_date.strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            not_found_count += 1
            print(f"Lead not found: {name} ({phone})")
    
    print(f"\nSummary:")
    print(f"Updated: {updated_count} leads")
    print(f"Not found: {not_found_count} leads")
    print(f"Total processed: {len([d for d in google_sheets_data if d['phone']])}")

if __name__ == "__main__":
    fix_google_sheets_dates()