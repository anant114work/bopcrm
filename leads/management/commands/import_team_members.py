from django.core.management.base import BaseCommand
from leads.models import TeamMember

class Command(BaseCommand):
    help = 'Import team members from predefined data'

    def handle(self, *args, **options):
        team_data = [
            {"name": "Aarti sharma", "email": "aarti.sharma@boprealty.com", "phone": "7669275936", "parent": "Mukul grover", "role": "BROKER"},
            {"name": "ABHIMANYU MEHRA", "email": "ABHIMANYU.MEHRA@BOPREALTY.COM", "phone": "9582201434", "parent": "gaurav gandhi", "role": "Sales Manager - T4"},
            {"name": "Abhishek gg", "email": "Abhishek@boprealty.com", "phone": "9711344640", "parent": "sandeep sethi gurugram", "role": "Sales Manager - T4"},
            {"name": "Abhishek singh rajput", "email": "abhirewarikhera@gmail.com", "phone": "8685815058", "parent": "sandeep sethi gurugram", "role": "Sales Manager - T4"},
            {"name": "Abhishek Choudhary", "email": "Abhishekkchoudhary726@gmail.com", "phone": "7065252433", "parent": "Yash Sharma", "role": "Sales Manager - T4"},
            {"name": "ABHISHEK KUMAR PM", "email": "ABHISHEK.KUMAR@BOPREALTY.COM", "phone": "9711141023", "parent": "payal", "role": "Sales Executive - T5"},
            {"name": "ABHISHEK prajapati", "email": "ABHISHEKPRAJAPATI248@GMAIL.COM", "phone": "9044497237", "parent": "AMIT KOHLI", "role": "Sales Manager - T4"},
            {"name": "Abhishek Tanwar", "email": "Abhishektanwar3636@gmail.com", "phone": "9911030299", "parent": "Himanshu kumar", "role": "BROKER"},
            {"name": "ABHISHEK VERMA", "email": "Abhishek.kumar608@yahoo.in", "phone": "7011039455", "parent": "ankit mavi", "role": "BROKER"},
            {"name": "Aditya Bhadana", "email": "Aditya.Bhadana@boprealty.com", "phone": "9355876240", "parent": "Vishal pandey", "role": "Sales Executive - T5"},
            {"name": "Admin", "email": "admin@gmail.com", "phone": "7290001154", "parent": "", "role": "Admin"},
            {"name": "AJAY PAL SINGH", "email": "AJAYPALSINGH@BOPREALTY.COM", "phone": "8800134520", "parent": "gaurav gandhi", "role": "Sales Manager - T4"},
            {"name": "Ajeet chaudhary", "email": "ajeet.chaudhary@boprealty.com", "phone": "8979167613", "parent": "Awadesh pateriya", "role": "BROKER"},
            {"name": "AJEET PRATAP SINGH", "email": "AJEETPRATAPSINGH@BOPREALTY.COM", "phone": "8588065313", "parent": "RAVISH SINGH", "role": "Team leader - t3"},
            {"name": "Alance Addhana", "email": "alanceaddhana1989@gmail.com", "phone": "9711141377", "parent": "ankit mavi", "role": "Sales Executive - T5"},
            {"name": "Alok Gahlot", "email": "alokkumargahlot2@gmail.com", "phone": "8383916450", "parent": "PAWAN BHATI", "role": "BROKER"},
            {"name": "amit bhati", "email": "amit.bhati@boprealty.com", "phone": "8510808164", "parent": "PRAVEEN KR SHARMA", "role": "Sales Executive - T5"},
            {"name": "AMIT KADYAN", "email": "akumar@mybop.in", "phone": "9811723442", "parent": "Ankush Kadyan", "role": "BROKER"},
            {"name": "AMIT KOHLI", "email": "AMITKOHLI@GMAIL.COM", "phone": "9873422211", "parent": "sandeep sethi gurugram", "role": "Sales Manager - T4"},
            {"name": "Amit Kumar Bainsla", "email": "bainsla2323@gmail.com", "phone": "9999956799", "parent": "Amit Kumar Bainsla", "role": "Sales Manager - T4"},
            {"name": "amit mavi", "email": "amit.mavi@boprealty.com", "phone": "8130040959", "parent": "Gaurav Mavi", "role": "Sales Director - T1"},
            {"name": "Amit Yadav", "email": "Amit Yadav@boprealty.com", "phone": "8076586732", "parent": "Vishal pandey", "role": "Sales Executive - T5"},
            {"name": "Anil rawat", "email": "anil.rawat@boprealty.com", "phone": "8800490096", "parent": "Commercial  User", "role": "Commercial"},
            {"name": "Anjali pandit", "email": "Anjali.pandit@boprealty.com", "phone": "9958460307", "parent": "MANIISH KUMAR DABREY", "role": "Sales Executive - T5"},
            {"name": "Anjali Singh", "email": "AnjaliSingh@BOPREALTY.COM", "phone": "8588062522", "parent": "JAGDISH", "role": "Sales Executive - T5"},
            {"name": "ankit mavi", "email": "ankit.mavi@boprealty.com", "phone": "9650633333", "parent": "SAURAV MAVI", "role": "TEAM Head - T2"},
            {"name": "ANKIT NAGAR", "email": "ANKIT.NAGAR@boprealty.com", "phone": "9582992022", "parent": "Sachin Mavi", "role": "Sales Manager - T4"},
            {"name": "Ankur Gupta", "email": "Lifeankurgupta@gmail.com", "phone": "7982339756", "parent": "Priyanka Kochhar", "role": "Sales Executive - T5"},
            {"name": "ANKUSH GAUTAM", "email": "ANKUSH.GAUTAM@BOPREALTY.COM", "phone": "8929535727", "parent": "Pratham Verma", "role": "Sales Executive - T5"},
            {"name": "Ankush Kadyan", "email": "ak@mybop.in", "phone": "9871627302", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "Gaurav Mavi", "email": "gv@mybop.in", "phone": "9910266552", "parent": "", "role": "Sales Director - T1"}
        ]
        
        # Create Gaurav Mavi first as he's the owner
        gaurav, created = TeamMember.objects.get_or_create(
            email="gv@mybop.in",
            defaults={
                "name": "Gaurav Mavi",
                "phone": "9910266552",
                "role": "Sales Director - T1",
                "parent_user": None
            }
        )
        
        if created:
            self.stdout.write(f"Created owner: {gaurav.name}")
        
        # Create other team members
        for member_data in team_data:
            if member_data["email"] == "gv@mybop.in":
                continue  # Skip Gaurav as already created
                
            parent = None
            if member_data["parent"]:
                try:
                    parent = TeamMember.objects.get(name__iexact=member_data["parent"])
                except TeamMember.DoesNotExist:
                    self.stdout.write(f"Parent not found: {member_data['parent']} for {member_data['name']}")
            
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
                self.stdout.write(f"Created: {member.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {TeamMember.objects.count()} team members'))