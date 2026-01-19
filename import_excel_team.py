#!/usr/bin/env python
import os
import sys
import django
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User
from leads.models import TeamMember

def import_from_excel():
    try:
        # Read the Excel file
        df = pd.read_excel('SALES USER LIST.xlsx')
        print(f"Found {len(df)} rows in Excel file")
        
        # Clear existing data
        print("Clearing existing team members...")
        TeamMember.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        
        imported_count = 0
        
        for index, row in df.iterrows():
            try:
                # Extract data from Excel row
                name = str(row.get('Name', '')).strip()
                email = str(row.get('Email', '')).strip()
                phone = str(row.get('Phone', '')).strip()
                role = str(row.get('Role', 'Sales Executive - T5')).strip()
                
                if not name or name == 'nan':
                    continue
                
                # Generate email if missing
                if not email or email == 'nan':
                    email = f"{name.lower().replace(' ', '.')}@boprealty.com"
                
                # Generate phone if missing
                if not phone or phone == 'nan':
                    phone = f"9999{str(index).zfill(6)}"
                
                # Create username
                username = name.split()[0].lower()
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{name.split()[0].lower()}{counter}"
                    counter += 1
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=phone,
                    first_name=name.split()[0],
                    last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                )
                
                # Create team member
                member = TeamMember.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    role=role,
                    parent_user=None,  # Set hierarchy later if needed
                    is_active=True
                )
                
                imported_count += 1
                print(f"Imported: {name} (user: {username})")
                
            except Exception as e:
                print(f"Error importing row {index}: {e}")
                continue
        
        print(f"\nSuccessfully imported {imported_count} team members")
        print(f"Total team members: {TeamMember.objects.count()}")
        print(f"Total users: {User.objects.count()}")
        
    except FileNotFoundError:
        print("Excel file 'SALES USER LIST.xlsx' not found!")
        print("Please make sure the file is in the project root directory")
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    import_from_excel()