from django.core.management.base import BaseCommand
from leads.models import TeamMember

class Command(BaseCommand):
    help = 'Import all 321 team members'

    def handle(self, *args, **options):
        # First create Gaurav Mavi as owner
        gaurav, created = TeamMember.objects.get_or_create(
            email="gv@mybop.in",
            defaults={
                "name": "Gaurav Mavi",
                "phone": "9910266552", 
                "role": "Sales Director - T1",
                "parent_user": None
            }
        )
        
        # Import in batches to avoid memory issues
        batch1 = [
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
            {"name": "Amit Kumar Bainsla", "email": "bainsla2323@gmail.com", "phone": "9999956799", "parent": "Amit Kumar Bainsla", "role": "Sales Manager - T4"}
        ]
        
        self._import_batch(batch1)
        self.stdout.write('Batch 1 imported')
        
    def _import_batch(self, batch_data):
        for member_data in batch_data:
            if member_data["email"] == "gv@mybop.in":
                continue
                
            parent = None
            if member_data["parent"]:
                try:
                    parent = TeamMember.objects.get(name__iexact=member_data["parent"])
                except TeamMember.DoesNotExist:
                    pass
            
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