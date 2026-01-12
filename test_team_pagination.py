#!/usr/bin/env python
"""
Test script for team pagination functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember
from django.core.paginator import Paginator

def test_team_pagination():
    """Test the team pagination functionality"""
    print("Testing Team Pagination Functionality")
    print("=" * 50)
    
    # Get all team members
    members = TeamMember.objects.all().order_by('name')
    total_count = members.count()
    
    print(f"Total team members: {total_count}")
    
    if total_count == 0:
        print("No team members found. Please add some team members first.")
        return
    
    # Test pagination
    paginator = Paginator(members, 12)  # 12 per page
    print(f"Total pages: {paginator.num_pages}")
    
    # Show first page
    page1 = paginator.get_page(1)
    print(f"\nPage 1 ({page1.start_index()}-{page1.end_index()} of {page1.paginator.count}):")
    
    for member in page1:
        status = "Active" if member.is_active else "Inactive"
        parent = f"Reports to: {member.parent_user.name}" if member.parent_user else "Team Lead"
        leads_count = member.assigned_leads.count() if hasattr(member, 'assigned_leads') else 0
        
        print(f"  - {member.name} ({member.role}) - {status} - {parent} - {leads_count} leads")
    
    # Test search functionality
    print(f"\nTesting search functionality...")
    search_term = "sales"
    filtered_members = members.filter(
        name__icontains=search_term
    ) | members.filter(
        role__icontains=search_term
    ) | members.filter(
        email__icontains=search_term
    )
    
    print(f"Members matching '{search_term}': {filtered_members.count()}")
    
    # Test role filtering
    roles = members.values_list('role', flat=True).distinct()
    print(f"\nAvailable roles: {list(roles)}")
    
    if roles:
        test_role = roles[0]
        role_filtered = members.filter(role=test_role)
        print(f"Members with role '{test_role}': {role_filtered.count()}")
    
    print("\n[SUCCESS] Team pagination test completed successfully!")

if __name__ == "__main__":
    test_team_pagination()