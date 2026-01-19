"""
Enhanced Team Hierarchy Management
"""
from django.db import models
from .models import TeamMember

class TeamHierarchy:
    """Manage team hierarchy and business head mapping"""
    
    # Business head roles (these are the top-level managers who have teams)
    BUSINESS_HEAD_ROLES = [
        'Admin',
        'Sales Director - T1', 
        'TEAM Head - T2'
    ]
    
    # Role hierarchy mapping (parent -> child roles)
    ROLE_HIERARCHY = {
        'Admin': ['Sales Director - T1', 'TEAM Head - T2'],
        'Sales Director - T1': ['TEAM Head - T2', 'Team leader - t3'],
        'TEAM Head - T2': ['Team leader - t3', 'Sales Manager - T4'],
        'Team leader - t3': ['Sales Manager - T4', 'Sales Executive - T5'],
        'Sales Manager - T4': ['Sales Executive - T5', 'Telecaller - T6'],
        'Sales Executive - T5': ['Telecaller - T6'],
        'Telecaller - T6': [],
        'BROKER': [],
        'Commercial': []
    }
    
    @classmethod
    def get_business_heads(cls):
        """Get all team members who are business heads"""
        return TeamMember.objects.filter(
            role__in=cls.BUSINESS_HEAD_ROLES,
            is_active=True
        ).order_by('role', 'name')
    
    @classmethod
    def get_unmapped_members(cls):
        """Get team members who don't have a parent assigned"""
        return TeamMember.objects.filter(
            parent_user__isnull=True,
            is_active=True
        ).exclude(role__in=cls.BUSINESS_HEAD_ROLES)
    
    @classmethod
    def get_hierarchy_tree(cls):
        """Get complete team hierarchy as nested structure"""
        business_heads = cls.get_business_heads()
        hierarchy = []
        
        for head in business_heads:
            head_data = {
                'member': head,
                'children': cls._get_children_recursive(head)
            }
            hierarchy.append(head_data)
        
        return hierarchy
    
    @classmethod
    def _get_children_recursive(cls, parent):
        """Recursively get all children under a parent"""
        children = TeamMember.objects.filter(
            parent_user=parent,
            is_active=True
        ).order_by('role', 'name')
        
        result = []
        for child in children:
            child_data = {
                'member': child,
                'children': cls._get_children_recursive(child)
            }
            result.append(child_data)
        
        return result
    
    @classmethod
    def suggest_parent_for_member(cls, member):
        """Suggest appropriate parent for a team member based on role hierarchy"""
        if member.role in cls.BUSINESS_HEAD_ROLES:
            return None  # Business heads don't need parents
        
        # Find potential parents based on role hierarchy
        potential_parents = []
        
        for parent_role, child_roles in cls.ROLE_HIERARCHY.items():
            if member.role in child_roles:
                parents = TeamMember.objects.filter(
                    role=parent_role,
                    is_active=True
                ).exclude(id=member.id)
                potential_parents.extend(parents)
        
        return potential_parents
    
    @classmethod
    def auto_assign_hierarchy(cls):
        """Automatically assign hierarchy based on role structure"""
        unmapped = cls.get_unmapped_members()
        assignments = []
        
        for member in unmapped:
            suggested_parents = cls.suggest_parent_for_member(member)
            if suggested_parents:
                # Assign to first available parent (can be enhanced with load balancing)
                suggested_parent = suggested_parents[0]
                assignments.append({
                    'member': member,
                    'suggested_parent': suggested_parent,
                    'confidence': 'high' if len(suggested_parents) == 1 else 'medium'
                })
            else:
                assignments.append({
                    'member': member,
                    'suggested_parent': None,
                    'confidence': 'manual_required'
                })
        
        return assignments
    
    @classmethod
    def get_team_stats(cls):
        """Get team hierarchy statistics"""
        total_members = TeamMember.objects.filter(is_active=True).count()
        business_heads = cls.get_business_heads().count()
        unmapped = cls.get_unmapped_members().count()
        
        # Calculate depth of hierarchy
        max_depth = 0
        for head in cls.get_business_heads():
            depth = cls._calculate_depth(head, 1)
            max_depth = max(max_depth, depth)
        
        return {
            'total_members': total_members,
            'business_heads': business_heads,
            'unmapped_members': unmapped,
            'max_hierarchy_depth': max_depth,
            'mapped_percentage': ((total_members - unmapped) / total_members * 100) if total_members > 0 else 0
        }
    
    @classmethod
    def _calculate_depth(cls, parent, current_depth):
        """Calculate maximum depth of hierarchy under a parent"""
        children = TeamMember.objects.filter(parent_user=parent, is_active=True)
        if not children.exists():
            return current_depth
        
        max_child_depth = current_depth
        for child in children:
            child_depth = cls._calculate_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth