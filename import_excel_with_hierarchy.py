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

def import_with_hierarchy():
    try:
        # Read the Excel file
        df = pd.read_excel('SALES USER LIST.xlsx')
        print(f"Found {len(df)} rows in Excel file")
        
        # Clear existing data
        print("Clearing existing team members...")
        TeamMember.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        
        # First pass: Create all members without parents
        print("Pass 1: Creating all members...")
        for index, row in df.iterrows():
            try:
                name = str(row.get('Name', '')).strip()
                email = str(row.get('Email', '')).strip()
                phone = str(row.get('Phone', '')).strip()
                role = str(row.get('Role', 'Sales Executive - T5')).strip()
                parent_name = str(row.get('Parent User', '')).strip()
                
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
                
                # Create team member without parent first
                member = TeamMember.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    role=role,
                    parent_user=None,  # Will set in second pass
                    is_active=True
                )
                
                print(f"Created: {name}")
                
            except Exception as e:
                print(f"Error creating {name}: {e}")
                continue
        
        # Second pass: Set parent relationships
        print("\nPass 2: Setting parent relationships...")
        df_with_parents = df[df['Parent User'].notna() & (df['Parent User'] != '')]
        
        for index, row in df_with_parents.iterrows():
            try:
                name = str(row.get('Name', '')).strip()
                parent_name = str(row.get('Parent User', '')).strip()
                
                if not name or not parent_name or name == 'nan' or parent_name == 'nan':
                    continue
                
                # Find the member and parent
                try:
                    member = TeamMember.objects.get(name=name)
                    parent = TeamMember.objects.get(name=parent_name)
                    
                    member.parent_user = parent
                    member.save()
                    
                    print(f"Set {name} -> reports to -> {parent_name}")
                    
                except TeamMember.DoesNotExist as e:
                    print(f"Could not find member or parent for {name} -> {parent_name}: {e}")
                    continue
                    
            except Exception as e:
                print(f"Error setting parent for {name}: {e}")
                continue
        
        # Summary
        total_members = TeamMember.objects.count()
        members_with_parents = TeamMember.objects.filter(parent_user__isnull=False).count()
        top_level_members = TeamMember.objects.filter(parent_user__isnull=True).count()
        
        print(f"\n=== IMPORT SUMMARY ===")
        print(f"Total members imported: {total_members}")
        print(f"Members with parents: {members_with_parents}")
        print(f"Top-level members: {top_level_members}")
        print(f"Total users created: {User.objects.count()}")
        
        # Show hierarchy
        print(f"\n=== TOP LEVEL MEMBERS ===")
        for member in TeamMember.objects.filter(parent_user__isnull=True):
            print(f"- {member.name} ({member.role})")
        
    except FileNotFoundError:
        print("Excel file 'SALES USER LIST.xlsx' not found!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import_with_hierarchy()