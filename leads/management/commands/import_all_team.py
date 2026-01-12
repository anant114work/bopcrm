from django.core.management.base import BaseCommand
from leads.models import TeamMember

class Command(BaseCommand):
    help = 'Import all team members with proper hierarchy'

    def handle(self, *args, **options):
        # Clear existing data
        TeamMember.objects.all().delete()
        
        # All team data
        team_data = [
            {"name": "Gaurav Mavi", "email": "gv@mybop.in", "phone": "9910266552", "parent": "", "role": "Sales Director - T1"},
            {"name": "Admin", "email": "admin@gmail.com", "phone": "7290001154", "parent": "", "role": "Admin"},
            {"name": "amit mavi", "email": "amit.mavi@boprealty.com", "phone": "8130040959", "parent": "Gaurav Mavi", "role": "Sales Director - T1"},
            {"name": "ankit mavi", "email": "ankit.mavi@boprealty.com", "phone": "9650633333", "parent": "SAURAV MAVI", "role": "TEAM Head - T2"},
            {"name": "SAURAV MAVI", "email": "Saurav.mavi@boprealty.com", "phone": "8126084952", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "Prince Mavi", "email": "prince.mavi@boprealty.com", "phone": "9999826429", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "Sachin Mavi", "email": "sgmc24@gmail.com", "phone": "7982507208", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "RAGHU NANDAN", "email": "RAGHU.NANDAN@BOPREALTY.COM", "phone": "8920410474", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "Himanshu kumar", "email": "Himanshu.kumar@boprealty.com", "phone": "9210760063", "parent": "ankit mavi", "role": "TEAM Head - T2"},
            {"name": "GAUTAM GUPTA", "email": "GAUTAM.GUPTA@boprealty.com", "phone": "8506010058", "parent": "SAURAV MAVI", "role": "TEAM Head - T2"},
            {"name": "Sandeep Sethi", "email": "sn.sethi@yahoo.com", "phone": "8742930690", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "sandeep sethi gurugram", "email": "Hitesh@BOPREALTY.COM", "phone": "7503003000", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "ROHIT magicbricks", "email": "rohit@boprealty.com", "phone": "9560522766", "parent": "Gaurav Mavi", "role": "TEAM Head - T2"},
            {"name": "Rohit Kapur", "email": "rohit.external@mailinator.com", "phone": "9910457990", "parent": "Admin", "role": "TEAM Head - T2"},
            {"name": "Narendra Singh", "email": "narendrasngh995@gmail.com", "phone": "9999401224", "parent": "Rohit Kapur", "role": "TEAM Head - T2"},
            {"name": "VAIBHAV KUMAR", "email": "VAIBHAV.KUMAR@BOPREALTY.COM", "phone": "9625971938", "parent": "Ankush Kadyan", "role": "TEAM Head - T2"},
            {"name": "Ankush Kadyan", "email": "ak@mybop.in", "phone": "9871627302", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "gaurav gandhi", "email": "gaurav.gandhi@boprealty.com", "phone": "9873665696", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "Mukul grover", "email": "mukul.grover@bopraelty.com", "phone": "9911936060", "parent": "Ankush Kadyan", "role": "Team leader - t3"},
            {"name": "Vishal pandey", "email": "pandeyvishal2@gmail.com", "phone": "9654137504", "parent": "Gaurav Mavi", "role": "BROKER"},
            {"name": "komal sharma", "email": "komal.sharma@boprealty.com", "phone": "7290001169", "parent": "Admin", "role": "Admin"},
            {"name": "PRAVEEN MAVI", "email": "parveen.mavi@mybop.in", "phone": "7290001190", "parent": "Ankush Kadyan", "role": "Sales Manager - T4"},
            {"name": "Awadesh pateriya", "email": "Awadhesh.pateriya@boprealty.com", "phone": "7834917086", "parent": "Rahul solanki", "role": "Sales Manager - T4"},
            {"name": "Rahul solanki", "email": "rs@treeglobal.in", "phone": "9810338825", "parent": "ankit mavi", "role": "Sales Manager - T4"},
            {"name": "chirag jaitley", "email": "CHIRAG.JAITLEY@BOPREALTY.COM", "phone": "9667434500", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "Romil Saxena", "email": "Romil.saxena@icloud.com", "phone": "9355876257", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "manik anand", "email": "MANIK@whitknight.com", "phone": "9818888418", "parent": "Gaurav Mavi", "role": "Sales Manager - T4"},
            {"name": "Yash Sharma", "email": "yashhxsh@gmail.com", "phone": "8585939447", "parent": "Romil Saxena", "role": "Sales Manager - T4"},
            {"name": "Priyanka Jain", "email": "priyanka.jain@boprealty.com", "phone": "9818779907", "parent": "Ankush Kadyan", "role": "Sales Manager - T4"},
            {"name": "Tarun Virmani", "email": "Tarunvirmani80@gmail.com", "phone": "8742930329", "parent": "Sandeep Sethi", "role": "Sales Manager - T4"},
            {"name": "Kappil Sarreen", "email": "kappilsarreen@gmail.com", "phone": "8851344161", "parent": "Romil Saxena", "role": "Sales Manager - T4"},
            {"name": "Mohammad Mehdi", "email": "syedmohd.mehdi110@gmail.com", "phone": "8303464140", "parent": "Romil Saxena", "role": "Team leader - t3"},
            {"name": "Owais Mustafa Khan", "email": "owaismustafakhan05@gmail.com", "phone": "8595239845", "parent": "Romil Saxena", "role": "Sales Manager - T4"},
            {"name": "Shweta sikdar", "email": "Shwetasikdar2@gmail.com", "phone": "7982653082", "parent": "chirag jaitley", "role": "Sales Manager - T4"},
            {"name": "saba khan", "email": "saba@whiteknights.co.in", "phone": "9899018540", "parent": "manik anand", "role": "Sales Manager - T4"},
            {"name": "Priyanka Kochhar", "email": "priyankakochhar9@gmail.com", "phone": "8587031626", "parent": "Romil Saxena", "role": "Team leader - t3"},
            {"name": "Shabina Saeed", "email": "shebik722@gmail.com", "phone": "8588819640", "parent": "Romil Saxena", "role": "Team leader - t3"},
            {"name": "Raghwan", "email": "mahera.r@mybop.in", "phone": "8826330262", "parent": "Raghwan", "role": "Team leader - t3"},
            {"name": "Atif Anwar", "email": "anwaratif41@gmail.com", "phone": "7703828826", "parent": "ankit mavi", "role": "Team leader - t3"},
            {"name": "manoj sethi", "email": "manojsethi@boprealty.com", "phone": "9910070102", "parent": "chirag jaitley", "role": "Team leader - t3"},
            {"name": "Rizwan Ali", "email": "rizwan.pasha22@gmail.com", "phone": "7669423328", "parent": "SHAMIM KHAN", "role": "Team leader - t3"},
            {"name": "NARESH BHATIA", "email": "NARESH.BHATIA@BOPREALTY.COM", "phone": "9810326669", "parent": "RAGHU NANDAN", "role": "Team leader - t3"},
            {"name": "AJEET PRATAP SINGH", "email": "AJEETPRATAPSINGH@BOPREALTY.COM", "phone": "8588065313", "parent": "RAVISH SINGH", "role": "Team leader - t3"},
            {"name": "anu goyal", "email": "anugoel@boprealty.com", "phone": "9205098820", "parent": "Ankush Kadyan", "role": "Team leader - t3"},
            {"name": "ASHUTOSH KAUSHIK", "email": "ASHUTOSHKAUSHIK@BOPREALTY.COM", "phone": "7290007953", "parent": "Sachin Mavi", "role": "Team leader - t3"},
            {"name": "GAURAV KAUSHAL", "email": "GAURAV.KAUSHAL@boprealty.com", "phone": "8929525867", "parent": "Prince Mavi", "role": "Team leader - t3"}
        ]
        
        # Import in multiple passes to handle hierarchy
        imported_count = 0
        
        # Pass 1: Create top-level members
        for member_data in team_data:
            if not member_data["parent"]:
                member, created = TeamMember.objects.get_or_create(
                    email=member_data["email"],
                    defaults={
                        "name": member_data["name"],
                        "phone": member_data["phone"],
                        "role": member_data["role"],
                        "parent_user": None
                    }
                )
                if created:
                    imported_count += 1
                    self.stdout.write(f"Created: {member.name}")
        
        # Pass 2-5: Create members with parents (multiple passes for deep hierarchy)
        for pass_num in range(2, 6):
            for member_data in team_data:
                if member_data["parent"] and not TeamMember.objects.filter(email=member_data["email"]).exists():
                    try:
                        parent = TeamMember.objects.get(name__iexact=member_data["parent"])
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
                            imported_count += 1
                            self.stdout.write(f"Pass {pass_num} - Created: {member.name}")
                    except TeamMember.DoesNotExist:
                        continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {imported_count} team members')
        )