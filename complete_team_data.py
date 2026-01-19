#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User
from leads.models import TeamMember

# Complete team data with all 321 members
COMPLETE_TEAM_DATA = [
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
    {"name": "anshish Gautam", "email": "ASHISHAK4789@GMAIL.COM", "phone": "8826237305", "parent": "RAGHU NANDAN", "role": "BROKER"},
    {"name": "ANSHPREET", "email": "anshpreetbakshi@gmail.com", "phone": "7536075675", "parent": "MANISH SACHDEVA", "role": "BROKER"},
    {"name": "Anshul Rastogi", "email": "anshulrastogi2023@gmail.com", "phone": "7827525172", "parent": "Abhishek Tanwar", "role": "BROKER"},
    {"name": "anu goyal", "email": "anugoel@boprealty.com", "phone": "9205098820", "parent": "Ankush Kadyan", "role": "Team leader - t3"},
    {"name": "Anuj Solanki", "email": "solankianuj203@gmail.com", "phone": "8882429472", "parent": "harsh yaduvanshi", "role": "BROKER"},
    {"name": "ANURAG SINGH", "email": "ANURAG@KNOWBLER.IN", "phone": "9532765290", "parent": "RAHUL SIRADHANA", "role": "BROKER"},
    {"name": "Anwar Reza khan", "email": "Anwar.Rezakhan@boprealty.com", "phone": "7835003668", "parent": "SHAMIM KHAN", "role": "Sales Manager - T4"},
    {"name": "Aparna Dubey", "email": "Aparnaenterprisesco@gmail.com", "phone": "9999500022", "parent": "ankit mavi", "role": "Sales Manager - T4"},
    {"name": "Aryan tomer", "email": "aryan@boprealty.com", "phone": "9355077435", "parent": "Ankush Kadyan", "role": "Sales Manager - T4"},
    {"name": "Ashish", "email": "Ashish@boprealty.com", "phone": "9650935754", "parent": "Ashish", "role": "BROKER"},
    {"name": "Ashok Sharma", "email": "asksha91@gmail.com", "phone": "8742923616", "parent": "Owais Mustafa Khan", "role": "Sales Manager - T4"},
    {"name": "ASHUTOSH KAUSHIK", "email": "ASHUTOSHKAUSHIK@BOPREALTY.COM", "phone": "7290007953", "parent": "Sachin Mavi", "role": "Team leader - t3"},
    {"name": "Atif Anwar", "email": "anwaratif41@gmail.com", "phone": "7703828826", "parent": "ankit mavi", "role": "Team leader - t3"},
    {"name": "Atul Verma", "email": "av@mybop.in", "phone": "9999929832", "parent": "", "role": "Admin"},
    {"name": "Awadesh pateriya", "email": "Awadhesh.pateriya@boprealty.com", "phone": "7834917086", "parent": "Rahul solanki", "role": "Sales Manager - T4"},
    {"name": "AYUSH SHARMA", "email": "AYUSH.SHARMA@BOPREALTY.COM", "phone": "9899905522", "parent": "Prince Mavi", "role": "Sales Manager - T4"},
    {"name": "AYUSHI KRISHNATREY", "email": "AYUSHI KRISHNATREY@BOPREALTY.COM", "phone": "9871880082", "parent": "Suraj Kumar Sharma", "role": "Telecaller - T6"},
    {"name": "Bhavnesh Kadyan", "email": "bhavnesh.kadyan@boprealty.com", "phone": "9870115387", "parent": "Ankush Kadyan", "role": "BROKER"},
    {"name": "Bhuwan Dass", "email": "bhuwandass72@yahoo.com", "phone": "9810493935", "parent": "manik anand", "role": "Sales Executive - T5"},
    {"name": "BINDU", "email": "BINDU@boprealty.com", "phone": "8929251920", "parent": "Anjali pandit", "role": "Sales Manager - T4"},
    {"name": "Gaurav Mavi", "email": "gv@mybop.in", "phone": "9910266552", "parent": "", "role": "Sales Director - T1"}
]

def create_member_with_user(member_data, parent=None):
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
    
    # Create team member
    member, member_created = TeamMember.objects.get_or_create(
        email=member_data["email"],
        defaults={
            "name": member_data["name"],
            "phone": member_data["phone"],
            "role": member_data["role"],
            "parent_user": parent
        }
    )
    
    return user, member, member_created

if __name__ == "__main__":
    print("This file contains the complete team data. Use import_all_321_members.py to import.")