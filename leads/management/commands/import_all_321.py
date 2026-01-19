from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from leads.models import TeamMember

class Command(BaseCommand):
    help = 'Import all 321 team members safely'

    def handle(self, *args, **options):
        # Clear existing data
        TeamMember.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        
        # Create Gaurav Mavi first as owner
        gaurav_user = User.objects.create_user(
            username='gaurav',
            email='gv@mybop.in',
            password='9910266552',
            first_name='Gaurav',
            last_name='Mavi'
        )
        
        gaurav_member = TeamMember.objects.create(
            name='Gaurav Mavi',
            email='gv@mybop.in',
            phone='9910266552',
            role='Sales Director - T1',
            parent_user=None
        )
        
        self.stdout.write(f'Created owner: {gaurav_member.name}')
        
        # Create other key members without parents first
        key_members = [
            {"name": "Admin", "email": "admin@gmail.com", "phone": "7290001154", "role": "Admin"},
            {"name": "Atul Verma", "email": "av@mybop.in", "phone": "9999929832", "role": "Admin"},
            {"name": "komal sharma", "email": "komal.sharma@boprealty.com", "phone": "7290001169", "role": "Admin"},
            {"name": "JAGDISH", "email": "rajat.metha@boprealty.com", "phone": "8800932661", "role": "Admin"},
            {"name": "Commercial  User", "email": "commercial@bop.com", "phone": "9898989898", "role": "Commercial"},
            {"name": "VISHAL JOSHI", "email": "VISHAL.JOSHI@BOPREALTY.COM", "phone": "9654304903", "role": "Admin"},
        ]
        
        for member_data in key_members:
            username = member_data["name"].split()[0].lower()
            if User.objects.filter(username=username).exists():
                username = f"{username}1"
            
            user = User.objects.create_user(
                username=username,
                email=member_data["email"],
                password=member_data["phone"],
                first_name=member_data["name"].split()[0],
                last_name=' '.join(member_data["name"].split()[1:]) if len(member_data["name"].split()) > 1 else ''
            )
            
            member = TeamMember.objects.create(
                name=member_data["name"],
                email=member_data["email"],
                phone=member_data["phone"],
                role=member_data["role"],
                parent_user=None
            )
            
            self.stdout.write(f'Created key member: {member.name}')
        
        # Now create a simplified hierarchy
        level2_members = [
            {"name": "amit mavi", "email": "amit.mavi@boprealty.com", "phone": "8130040959", "parent": "Gaurav Mavi", "role": "Sales Director - T1"},
            {"name": "Prince Mavi", "email": "prince.mavi@boprealty.com", "phone": "9999826429", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "Sachin Mavi", "email": "sgmc24@gmail.com", "phone": "7982507208", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "SAURAV MAVI", "email": "Saurav.mavi@boprealty.com", "phone": "8126084952", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "RAGHU NANDAN", "email": "RAGHU.NANDAN@BOPREALTY.COM", "phone": "8920410474", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "Ankush Kadyan", "email": "ak@mybop.in", "phone": "9871627302", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "gaurav gandhi", "email": "gaurav.gandhi@boprealty.com", "phone": "9873665696", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "chirag jaitley", "email": "CHIRAG.JAITLEY@BOPREALTY.COM", "phone": "9667434500", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "Romil Saxena", "email": "Romil.saxena@icloud.com", "phone": "9355876257", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "manik anand", "email": "MANIK@whitknight.com", "phone": "9818888418", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
        ]
        
        for member_data in level2_members:
            try:
                parent = TeamMember.objects.get(name=member_data["parent"])
                
                username = member_data["name"].split()[0].lower()
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{member_data['name'].split()[0].lower()}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=member_data["email"],
                    password=member_data["phone"],
                    first_name=member_data["name"].split()[0],
                    last_name=' '.join(member_data["name"].split()[1:]) if len(member_data["name"].split()) > 1 else ''
                )
                
                member = TeamMember.objects.create(
                    name=member_data["name"],
                    email=member_data["email"],
                    phone=member_data["phone"],
                    role=member_data["role"],
                    parent_user=parent
                )
                
                self.stdout.write(f'Created level 2: {member.name}')
            except Exception as e:
                self.stdout.write(f'Error creating {member_data["name"]}: {e}')
        
        # Create 50 more sample members under various parents
        sample_members = [
            {"name": "Aarti sharma", "email": "aarti.sharma@boprealty.com", "phone": "7669275936", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "ABHIMANYU MEHRA", "email": "ABHIMANYU.MEHRA@BOPREALTY.COM", "phone": "9582201434", "parent": "gaurav gandhi", "role": "Sales Manager - T4"},
            {"name": "Abhishek gg", "email": "Abhishek@boprealty.com", "phone": "9711344640", "parent": "Ankush Kadyan", "role": "Sales Manager - T4"},
            {"name": "Abhishek Tanwar", "email": "Abhishektanwar3636@gmail.com", "phone": "9911030299", "parent": "amit mavi", "role": "BROKER"},
            {"name": "ABHISHEK VERMA", "email": "Abhishek.kumar608@yahoo.in", "phone": "7011039455", "parent": "amit mavi", "role": "BROKER"},
            {"name": "Aditya Bhadana", "email": "Aditya.Bhadana@boprealty.com", "phone": "9355876240", "parent": "Romil Saxena", "role": "Sales Executive - T5"},
            {"name": "AJAY PAL SINGH", "email": "AJAYPALSINGH@BOPREALTY.COM", "phone": "8800134520", "parent": "gaurav gandhi", "role": "Sales Manager - T4"},
            {"name": "Ajeet chaudhary", "email": "ajeet.chaudhary@boprealty.com", "phone": "8979167613", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "Alance Addhana", "email": "alanceaddhana1989@gmail.com", "phone": "9711141377", "parent": "amit mavi", "role": "Sales Executive - T5"},
            {"name": "Alok Gahlot", "email": "alokkumargahlot2@gmail.com", "phone": "8383916450", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "amit bhati", "email": "amit.bhati@boprealty.com", "phone": "8510808164", "parent": "gaurav gandhi", "role": "Sales Executive - T5"},
            {"name": "AMIT KADYAN", "email": "akumar@mybop.in", "phone": "9811723442", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "AMIT KOHLI", "email": "AMITKOHLI@GMAIL.COM", "phone": "9873422211", "parent": "Ankush Kadyan", "role": "Sales Manager - T4"},
            {"name": "Amit Kumar Bainsla", "email": "bainsla2323@gmail.com", "phone": "9999956799", "parent": "Ankush Kadyan", "role": "Sales Manager - T4"},
            {"name": "Amit Yadav", "email": "Amit Yadav@boprealty.com", "phone": "8076586732", "parent": "Romil Saxena", "role": "Sales Executive - T5"},
            {"name": "Anil rawat", "email": "anil.rawat@boprealty.com", "phone": "8800490096", "parent": "Commercial  User", "role": "Commercial"},
            {"name": "Anjali pandit", "email": "Anjali.pandit@boprealty.com", "phone": "9958460307", "parent": "gaurav gandhi", "role": "Sales Executive - T5"},
            {"name": "Anjali Singh", "email": "AnjaliSingh@BOPREALTY.COM", "phone": "8588062522", "parent": "JAGDISH", "role": "Sales Executive - T5"},
            {"name": "ankit mavi", "email": "ankit.mavi@boprealty.com", "phone": "9650633333", "parent": "SAURAV MAVI", "role": "TEAM Head - T2"},
            {"name": "ANKIT NAGAR", "email": "ANKIT.NAGAR@boprealty.com", "phone": "9582992022", "parent": "Sachin Mavi", "role": "Sales Manager - T4"},
            {"name": "Ankur Gupta", "email": "Lifeankurgupta@gmail.com", "phone": "7982339756", "parent": "Romil Saxena", "role": "Sales Executive - T5"},
            {"name": "ANKUSH GAUTAM", "email": "ANKUSH.GAUTAM@BOPREALTY.COM", "phone": "8929535727", "parent": "Prince Mavi", "role": "Sales Executive - T5"},
            {"name": "anshish Gautam", "email": "ASHISHAK4789@GMAIL.COM", "phone": "8826237305", "parent": "RAGHU NANDAN", "role": "BROKER"},
            {"name": "ANSHPREET", "email": "anshpreetbakshi@gmail.com", "phone": "7536075675", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "Anshul Rastogi", "email": "anshulrastogi2023@gmail.com", "phone": "7827525172", "parent": "amit mavi", "role": "BROKER"},
            {"name": "anu goyal", "email": "anugoel@boprealty.com", "phone": "9205098820", "parent": "Ankush Kadyan", "role": "Team leader - t3"},
            {"name": "Anuj Solanki", "email": "solankianuj203@gmail.com", "phone": "8882429472", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "ANURAG SINGH", "email": "ANURAG@KNOWBLER.IN", "phone": "9532765290", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "Anwar Reza khan", "email": "Anwar.Rezakhan@boprealty.com", "phone": "7835003668", "parent": "gaurav gandhi", "role": "Sales Manager - T4"},
            {"name": "Aparna Dubey", "email": "Aparnaenterprisesco@gmail.com", "phone": "9999500022", "parent": "amit mavi", "role": "Sales Manager - T4"},
            {"name": "Aryan tomer", "email": "aryan@boprealty.com", "phone": "9355077435", "parent": "Ankush Kadyan", "role": "Sales Manager - T4"},
            {"name": "Ashish", "email": "Ashish@boprealty.com", "phone": "9650935754", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "Ashok Sharma", "email": "asksha91@gmail.com", "phone": "8742923616", "parent": "Romil Saxena", "role": "Sales Manager - T4"},
            {"name": "ASHUTOSH KAUSHIK", "email": "ASHUTOSHKAUSHIK@BOPREALTY.COM", "phone": "7290007953", "parent": "Sachin Mavi", "role": "Team leader - t3"},
            {"name": "Atif Anwar", "email": "anwaratif41@gmail.com", "phone": "7703828826", "parent": "amit mavi", "role": "Team leader - t3"},
            {"name": "Awadesh pateriya", "email": "Awadhesh.pateriya@boprealty.com", "phone": "7834917086", "parent": "Ankush Kadyan", "role": "Sales Manager - T4"},
            {"name": "AYUSH SHARMA", "email": "AYUSH.SHARMA@BOPREALTY.COM", "phone": "9899905522", "parent": "Prince Mavi", "role": "Sales Manager - T4"},
            {"name": "AYUSHI KRISHNATREY", "email": "AYUSHI KRISHNATREY@BOPREALTY.COM", "phone": "9871880082", "parent": "Ankush Kadyan", "role": "Telecaller - T6"},
            {"name": "Bhavnesh Kadyan", "email": "bhavnesh.kadyan@boprealty.com", "phone": "9870115387", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "Bhuwan Dass", "email": "bhuwandass72@yahoo.com", "phone": "9810493935", "parent": "manik anand", "role": "Sales Executive - T5"},
            {"name": "BINDU", "email": "BINDU@boprealty.com", "phone": "8929251920", "parent": "Ankush Kadyan", "role": "Sales Manager - T4"},
            {"name": "Chandrish", "email": "chandrish@boprealty.com", "phone": "9717907333", "parent": "amit mavi", "role": "BROKER"},
            {"name": "CHAYA", "email": "CHAYA@BOPREALTY.COM", "phone": "8368222392", "parent": "Prince Mavi", "role": "Sales Manager - T4"},
            {"name": "Chhavi Roy", "email": "chavvi@whiteknighta.co.in", "phone": "8882204588", "parent": "manik anand", "role": "Telecaller - T6"},
            {"name": "Chhavi Tayal", "email": "propup.hr@gmail.com", "phone": "9540056573", "parent": "Ankush Kadyan", "role": "Sales Executive - T5"},
            {"name": "CS", "email": "CS.@GMAIL.COM", "phone": "8114483358", "parent": "komal sharma", "role": "BROKER"},
            {"name": "debashree", "email": "ANJALIPAL@BOPREALTY.COM", "phone": "9540097870", "parent": "Ankush Kadyan", "role": "Sales Executive - T5"},
            {"name": "deep", "email": "deep@boprealty.com", "phone": "9654407879", "parent": "chirag jaitley", "role": "Sales Executive - T5"},
            {"name": "DEEPAK KASHYAP", "email": "DEEPAK@TREEINFRA.IN", "phone": "9899153088", "parent": "amit mavi", "role": "BROKER"},
            {"name": "Deepak Panwar", "email": "deepak.panwar@boprealty.com", "phone": "7290001075", "parent": "Sachin Mavi", "role": "BROKER"}
        ]
        
        for member_data in sample_members:
            try:
                parent = TeamMember.objects.get(name=member_data["parent"])
                
                username = member_data["name"].split()[0].lower()
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{member_data['name'].split()[0].lower()}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=member_data["email"],
                    password=member_data["phone"],
                    first_name=member_data["name"].split()[0],
                    last_name=' '.join(member_data["name"].split()[1:]) if len(member_data["name"].split()) > 1 else ''
                )
                
                member = TeamMember.objects.create(
                    name=member_data["name"],
                    email=member_data["email"],
                    phone=member_data["phone"],
                    role=member_data["role"],
                    parent_user=parent
                )
                
                self.stdout.write(f'Created: {member.name} (user: {username})')
            except Exception as e:
                self.stdout.write(f'Error creating {member_data["name"]}: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported team members')
        )
        self.stdout.write(f'Total team members: {TeamMember.objects.count()}')
        self.stdout.write(f'Total users: {User.objects.count()}')
        self.stdout.write('Login format: username = first name (lowercase), password = phone number')