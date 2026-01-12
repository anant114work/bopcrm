#!/usr/bin/env python
import os
import sys
import django
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember

def set_hierarchy():
    try:
        df = pd.read_excel('SALES USER LIST.xlsx')
        print(f"Setting hierarchy for existing members...")
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                name = str(row.get('Name', '')).strip()
                parent_name = str(row.get('Parent User', '')).strip()
                
                if not name or name == 'nan' or not parent_name or parent_name == 'nan':
                    continue
                
                # Find member and parent
                try:
                    member = TeamMember.objects.get(name=name)
                    parent = TeamMember.objects.get(name=parent_name)
                    
                    member.parent_user = parent
                    member.save()
                    
                    print(f"OK: {name} -> {parent_name}")
                    success_count += 1
                    
                except TeamMember.DoesNotExist:
                    print(f"ERROR: Could not find: {name} or {parent_name}")
                    error_count += 1
                    
            except Exception as e:
                print(f"ERROR: {name}: {e}")
                error_count += 1
        
        print(f"\n=== HIERARCHY SUMMARY ===")
        print(f"Successfully set: {success_count}")
        print(f"Errors: {error_count}")
        
        # Show final counts
        total = TeamMember.objects.count()
        with_parents = TeamMember.objects.filter(parent_user__isnull=False).count()
        top_level = TeamMember.objects.filter(parent_user__isnull=True).count()
        
        print(f"Total members: {total}")
        print(f"With parents: {with_parents}")
        print(f"Top-level: {top_level}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    set_hierarchy()