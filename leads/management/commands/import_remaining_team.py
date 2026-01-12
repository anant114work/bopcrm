from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from leads.models import TeamMember

class Command(BaseCommand):
    help = 'Import remaining team members (batch 2-7)'

    def handle(self, *args, **options):
        # Batch 2 - Members 51-100
        team_data_batch2 = [
            {"name": "Chandrish", "email": "chandrish@boprealty.com", "phone": "9717907333", "parent": "ankit mavi", "role": "BROKER"},
            {"name": "CHAYA", "email": "CHAYA@BOPREALTY.COM", "phone": "8368222392", "parent": "Pratham Verma", "role": "Sales Manager - T4"},
            {"name": "Chhavi Roy", "email": "chavvi@whiteknighta.co.in", "phone": "8882204588", "parent": "saba khan", "role": "Telecaller - T6"},
            {"name": "Chhavi Tayal", "email": "propup.hr@gmail.com", "phone": "9540056573", "parent": "Aparna Dubey", "role": "Sales Executive - T5"},
            {"name": "chirag jaitley", "email": "CHIRAG.JAITLEY@BOPREALTY.COM", "phone": "9667434500", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "Commercial  User", "email": "commercial@bop.com", "phone": "9898989898", "parent": "Admin", "role": "Commercial"},
            {"name": "CS", "email": "CS.@GMAIL.COM", "phone": "8114483358", "parent": "komal sharma", "role": "BROKER"},
            {"name": "debashree", "email": "ANJALIPAL@BOPREALTY.COM", "phone": "9540097870", "parent": "Aarti sharma", "role": "Sales Executive - T5"},
            {"name": "deep", "email": "deep@boprealty.com", "phone": "9654407879", "parent": "chirag jaitley", "role": "Sales Executive - T5"},
            {"name": "DEEPAK KASHYAP", "email": "DEEPAK@TREEINFRA.IN", "phone": "9899153088", "parent": "ankit mavi", "role": "BROKER"},
            {"name": "Deepak Panwar", "email": "deepak.panwar@boprealty.com", "phone": "7290001075", "parent": "Sachin Mavi", "role": "BROKER"},
            {"name": "deepak seth", "email": "vishalbro999@gmail.com", "phone": "7011356405", "parent": "Shweta sikdar", "role": "Sales Executive - T5"},
            {"name": "Deepakshi tyagi", "email": "deepakshityagi28@gmail.com", "phone": "9690930829", "parent": "sandeep sethi gurugram", "role": "Sales Manager - T4"},
            {"name": "Deepika", "email": "Deepika@boprealty.com", "phone": "9958445033", "parent": "SHARAD GOEL", "role": "Sales Executive - T5"},
            {"name": "DEEPTI DHINGRA", "email": "DEEPTI@BOPREALTY.COM", "phone": "9873181415", "parent": "komal sharma", "role": "BROKER"},
            {"name": "DEV YADAV", "email": "DEVINTERIOR10@GMAIL.COM", "phone": "9958905056", "parent": "", "role": "Sales Executive - T5"},
            {"name": "Devashish", "email": "Devashish@boprealty.com", "phone": "7838486517", "parent": "Himanshu kumar", "role": "BROKER"},
            {"name": "Devendra Joshi", "email": "samratsharma327@gmail.com", "phone": "8860100407", "parent": "Kappil Sarreen", "role": "Sales Manager - T4"},
            {"name": "Dipak Kumar", "email": "dkkumarkcs@gmail.com", "phone": "9953074229", "parent": "Pavan Kumar", "role": "Sales Manager - T4"},
            {"name": "DISHA SHUKLA", "email": "DISHASHUKLAOCT@GMAIL.COM", "phone": "9319042854", "parent": "", "role": "BROKER"},
            {"name": "Dolly", "email": "dolly.sodhi17@gmail.com", "phone": "8860100594", "parent": "Romil Saxena", "role": "Sales Manager - T4"},
            {"name": "DUSHYANT BAKSHI", "email": "DUSHYANT.BAKSHI@boprealty.com", "phone": "9355891616", "parent": "DUSHYANT BAKSHI", "role": "Sales Manager - T4"},
            {"name": "GAURAV PM", "email": "GAURAV@BOPREALTY.COM", "phone": "9359359659", "parent": "AYUSH SHARMA", "role": "BROKER"},
            {"name": "GAURAV BENIWAL", "email": "GAURAV.BENIWAL@BOPREALTY.COM", "phone": "8929535322", "parent": "Anjali pandit", "role": "Sales Executive - T5"},
            {"name": "GAURAV BISIT", "email": "GAURAV.BISIT@boprealty.com", "phone": "8929738341", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "gaurav gandhi", "email": "gaurav.gandhi@boprealty.com", "phone": "9873665696", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "GAURAV KAUSHAL", "email": "GAURAV.KAUSHAL@boprealty.com", "phone": "8929525867", "parent": "Prince Mavi", "role": "Team leader - t3"},
            {"name": "Gaurav Khanna", "email": "GAURAV.KHANNA@BOPREALTY.COM", "phone": "7669423327", "parent": "LALIT SAREN", "role": "Sales Manager - T4"},
            {"name": "Gaurav Mavi", "email": "gv@mybop.in", "phone": "9910266552", "parent": "", "role": "Sales Director - T1"},
            {"name": "GAURAV SHARMA", "email": "INFRA.WORLD@GMAIL.COM", "phone": "9717260536", "parent": "", "role": "BROKER"},
            {"name": "Gaurav yadav", "email": "gaurav.yadav@gmail.com", "phone": "9806231837", "parent": "Pratham Verma", "role": "BROKER"},
            {"name": "Gauri narain", "email": "naraingauri798@gmail.com", "phone": "9289179438", "parent": "AMIT KOHLI", "role": "Sales Executive - T5"},
            {"name": "GAUTAM GUPTA", "email": "GAUTAM.GUPTA@boprealty.com", "phone": "8506010058", "parent": "SAURAV MAVI", "role": "TEAM Head - T2"},
            {"name": "gopal pandey", "email": "gopal.pandey@boprealty.com", "phone": "9811109677", "parent": "komal sharma", "role": "BROKER"},
            {"name": "HARSH", "email": "HARSH@BOPREALTY.COM", "phone": "9810140207", "parent": "SHARAD GOEL", "role": "Sales Manager - T4"},
            {"name": "Harsh Choudhary", "email": "Harshhhchoudhary@gmail.com", "phone": "7290049257", "parent": "Tarun Virmani", "role": "Sales Manager - T4"},
            {"name": "harsh yaduvanshi", "email": "harsh.yaduvanshi3325@gmail.com", "phone": "9999353065", "parent": "Himanshu kumar", "role": "Sales Manager - T4"},
            {"name": "have on deal", "email": "haveondeal.@boprealty.com", "phone": "9711360152", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "Himanshu kumar", "email": "Himanshu.kumar@boprealty.com", "phone": "9210760063", "parent": "ankit mavi", "role": "TEAM Head - T2"},
            {"name": "hitesh et now", "email": "hitesh@boprealty.com", "phone": "9599669218", "parent": "komal sharma", "role": "BROKER"},
            {"name": "HUSSAIN ABBAS", "email": "HUSSAINABBAS11072@GMAIL.COM", "phone": "7870666587", "parent": "", "role": "BROKER"},
            {"name": "Irfan Saifi", "email": "irfan.is2007@gmail.com", "phone": "9540056437", "parent": "Atif Anwar", "role": "Sales Executive - T5"},
            {"name": "ISHANK ANAND", "email": "ISHANKANAND@BOPREALTY.COM", "phone": "9711512889", "parent": "Prince Mavi", "role": "Sales Manager - T4"},
            {"name": "ISHIKA", "email": "sethishu2531@gmail.com", "phone": "8368519687", "parent": "MANISH SACHDEVA", "role": "BROKER"},
            {"name": "JAGDISH", "email": "rajat.metha@boprealty.com", "phone": "8800932661", "parent": "Gaurav Mavi", "role": "Admin"},
            {"name": "jagmender kumar", "email": "kabirjangra15@gmail.com", "phone": "9817819228", "parent": "Romil Saxena", "role": "Sales Manager - T4"},
            {"name": "JATIN A", "email": "Jatin.654@gmail.com", "phone": "9540781616", "parent": "ankit mavi", "role": "Sales Manager - T4"},
            {"name": "JATIN SHARMA", "email": "JATIN.SHARMA@BOPREALTY.COM", "phone": "7669233471", "parent": "RAGHU NANDAN", "role": "Sales Manager - T4"},
            {"name": "JITENDER KHARI", "email": "JITENDERKHARI@BOPREALTY.COM", "phone": "7838802259", "parent": "AJAY PAL SINGH", "role": "Sales Executive - T5"},
            {"name": "Jitendra Sharma", "email": "Sharmajatin10@gmail.com", "phone": "9899944450", "parent": "sandeep sethi gurugram", "role": "Sales Manager - T4"}
        ]
        
        self._import_batch(team_data_batch2, 2)
        self.stdout.write('Batch 2 completed (50 more members)')
        
    def _import_batch(self, batch_data, batch_num):
        for member_data in batch_data:
            # Create user account
            username = member_data["name"].split()[0].lower()
            password = member_data["phone"]
            
            # Handle duplicate usernames
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': member_data["email"],
                    'first_name': member_data["name"].split()[0],
                    'last_name': ' '.join(member_data["name"].split()[1:]) if len(member_data["name"].split()) > 1 else ''
                }
            )
            
            if user_created:
                user.set_password(password)
                user.save()
            
            # Find parent
            parent = None
            if member_data["parent"]:
                try:
                    parent = TeamMember.objects.get(name__iexact=member_data["parent"])
                except TeamMember.DoesNotExist:
                    pass
            
            # Create team member
            member, created = TeamMember.objects.get_or_create(
                email=member_data["email"],
                defaults={
                    "name": member_data["name"],
                    "phone": member_data["phone"],
                    "role": member_data["role"],
                    "parent_user": parent
                }
            )
            
            if created:
                self.stdout.write(f"Created: {member.name} (user: {username})")