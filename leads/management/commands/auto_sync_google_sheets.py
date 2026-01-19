from django.core.management.base import BaseCommand
from django.utils import timezone
from leads.models import Lead
import requests
import csv
import io
from datetime import datetime
import pytz

class Command(BaseCommand):
    help = 'Auto-sync Google Sheets leads every 5 minutes'

    def handle(self, *args, **options):
        SPREADSHEET_ID = '1tBO3sEET72uIJbdK2hixCCq4IicAv0eJxScWrnHzqMM'
        
        try:
            csv_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0'
            response = requests.get(csv_url)
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to fetch sheet: {response.status_code}'))
                return
            
            csv_data = csv.DictReader(io.StringIO(response.text))
            
            success_count = 0
            duplicate_count = 0
            
            for row in csv_data:
                try:
                    name = row.get('Name', '').strip()
                    phone = row.get('Phone', '').strip()
                    email = row.get('Email', '').strip().replace('mailto:', '')
                    unit_size = row.get('Unit Size', '').strip()
                    project = row.get('Project Name', '').strip()
                    timestamp = row.get('Date & Time', '').strip()
                    
                    if not name or not phone:
                        continue
                    
                    phone = phone.replace('+', '').replace(' ', '').replace('-', '')
                    if len(phone) > 10:
                        phone = phone[-10:]
                    
                    variants = [phone, f"+91{phone}", f"91{phone}"]
                    
                    if Lead.objects.filter(phone_number__in=variants).exists():
                        duplicate_count += 1
                        continue
                    
                    ist = pytz.timezone('Asia/Kolkata')
                    try:
                        if '/' in timestamp and ':' in timestamp:
                            dt = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
                            created = ist.localize(dt)
                        elif '/' in timestamp:
                            dt = datetime.strptime(timestamp, '%d/%m/%Y')
                            created = ist.localize(dt)
                        else:
                            created = timezone.now()
                    except:
                        created = timezone.now()
                    
                    lead_id = f"GS_SPJ_{created.strftime('%Y%m%d_%H%M%S')}_{phone[-4:]}"
                    
                    Lead.objects.create(
                        lead_id=lead_id,
                        full_name=name,
                        phone_number=f"+91{phone}",
                        email=email,
                        configuration=unit_size,
                        form_name=f"Google Sheets - {project}",
                        source='Google Sheets',
                        created_time=created,
                        extra_fields={
                            'unit_size': unit_size,
                            'project_name': project,
                            'original_timestamp': timestamp
                        }
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(f'Auto-sync completed: {success_count} new, {duplicate_count} duplicates')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Auto-sync failed: {str(e)}')
            )

# Old hardcoded data removed
if False:
    sample_leads = [
                {'name': 'ruchipanna tiwari', 'phone': '7058792708', 'email': 'pannachauhan53@gmail.com', 'project_name': 'Aspire Leisure Valley', 'date': '12/12/2025'},
                {'name': 'Subhash', 'phone': '9650296565', 'email': 'SUBHASHCHANDRA0512@GMAIL.COM', 'project_name': 'Aspire Leisure Valley', 'date': '12/12/2025'},
                {'name': 'Sarjeet Singh', 'phone': '9810805648', 'email': 'sarjeet01@yahoo.co.in', 'project_name': 'Aspire Leisure Valley', 'date': '12/12/2025'},
                {'name': 'Roseline Wilfred', 'phone': '9999715025', 'email': 'roselinewilfred1954@gmail.com', 'project_name': 'Aspire Leisure Valley', 'date': '12/12/2025'},
                {'name': 'Satish', 'phone': '9910487432', 'email': 'edqacskp@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Amit Kumar', 'phone': '9716881663', 'email': 'amitenjoyable@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Anju Kaushik', 'phone': '9650189757', 'email': 'anjukaushik79@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Dhiresh Malik', 'phone': '9999710075', 'email': 'dhiresh25@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Anirudh', 'phone': '9811868611', 'email': '', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Vikas Malhotra', 'phone': '9212109002', 'email': 'vksmal@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Kheem singh', 'phone': '9891341347', 'email': 'singhkheem17@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Rohit', 'phone': '9911414353', 'email': 'indusharma@123g.mai', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Keshav chand Rustagi', 'phone': '9810095590', 'email': 'keshav.rustagi@yahoo.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Hemendra', 'phone': '9818648647', 'email': '', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Anil', 'phone': '8510098308', 'email': 'anilbhati2308@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Uday Shankar sahay', 'phone': '9973760787', 'email': '', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Sksinha', 'phone': '9818612928', 'email': 'SKSinhadelhi@yahoo.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Amit Tiwary', 'phone': '9015190562', 'email': 'Amittiwaryca@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Ajay Gambhir', 'phone': '9311557085', 'email': 'drajaygambhir@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'A K Pandey', 'phone': '9899186170', 'email': 'ashwini.pandey@live.in', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Kritika Tewani', 'phone': '9818725777', 'email': 'anukriti.bindal@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Raghvendra Kumar yadav', 'phone': '8999633887', 'email': '', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Animesh Sinha', 'phone': '9999464305', 'email': 'sinha.animesh@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Hemant gogari', 'phone': '9403648123', 'email': 'hemant.gogari@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Chirag Bansal', 'phone': '9999228828', 'email': 'chiragbansal@greyradius.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Ankur Gupta', 'phone': '9643825852', 'email': 'ankur.jiitn@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Ankur Gupta', 'phone': '9650169018', 'email': 'ankur.jiitqn@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Saurabh chauhan', 'phone': '9313182779', 'email': 'Saurabhc0007@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Vinod', 'phone': '9540486936', 'email': 'singhvinod915@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Vinod', 'phone': '9540486939', 'email': 'singhvinod915@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Sachin Chauhan', 'phone': '8130538451', 'email': 'sachinamutech@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'OM PRAKASH MISHRA', 'phone': '9313003650', 'email': 'mishraop62@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'abcd jain', 'phone': '9811110000', 'email': 'abc@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Harsh Juneja', 'phone': '8383057087', 'email': 'harsh1028@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Anand', 'phone': '9810098100', 'email': 'anand@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Praveen', 'phone': '9999817982', 'email': 'praveenarunajain@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Pankaj kumar', 'phone': '8337078107', 'email': 'pksinha.alb@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Ankit KUMAR', 'phone': '8419994584', 'email': 'raghavankit47@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Kasturi Lal Bhatia', 'phone': '8447094562', 'email': 'enterneelam@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Sachin dua', 'phone': '9313531451', 'email': 'duasachin198578@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'vikas', 'phone': '9873733868', 'email': 'mac.timar@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Jay singh', 'phone': '9560054540', 'email': 'vijaygglobal@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Umesh Gupta', 'phone': '9602713139', 'email': 'umeshg2011@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Ashok Gupta', 'phone': '8851484031', 'email': 'akgupta0505@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Anand lal', 'phone': '9212555818', 'email': 'lalandsons7@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'C K Joseph', 'phone': '9811900711', 'email': 'ckjoseph59@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Ayush Tiwari', 'phone': '8340477897', 'email': 'ayushrajgaurmukh12345@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Saurabh', 'phone': '8447738612', 'email': 'srbhsethi1990@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Harshit Surana', 'phone': '7678186306', 'email': 'hrshtsurana10@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Puneet Khanna', 'phone': '9312890289', 'email': 'dnkshalini@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Karamveer awana', 'phone': '9958434142', 'email': 'kvawana570@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Arun', 'phone': '9650997257', 'email': 'varun41777@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Nitish', 'phone': '7906704502', 'email': 'nitish.vashishth@icloud.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Santosh Kumar Thakur', 'phone': '8929570323', 'email': 'santoshjithakur1985@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Farman Saifi', 'phone': '9027392542', 'email': 'farmansaifivlogs@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Abhishek Mishra', 'phone': '9015123888', 'email': 'abhishekm300@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Arun Chhabra', 'phone': '9650997257', 'email': 'varun41777@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Shreya', 'phone': '7340858013', 'email': 'prakashshreya0904@gmail.com', 'project_name': 'Aspire Leisure Valley'},
                {'name': 'Anil', 'phone': '9990279946', 'email': 'pugalia.anil@gmail.com', 'project_name': 'Aspire Leisure Valley'},
    ]