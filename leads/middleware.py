from django.utils.deprecation import MiddlewareMixin
from .models import LeadViewActivity, Lead, TeamMember
import re

class LeadViewTrackingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Only track successful GET requests to lead detail pages
        if (request.method == 'GET' and 
            response.status_code == 200 and 
            hasattr(request, 'session') and 
            request.session.get('team_member_id')):
            
            # Check if this is a lead detail page
            lead_detail_pattern = re.match(r'/leads/(\d+)/', request.path)
            if lead_detail_pattern:
                lead_id = lead_detail_pattern.group(1)
                team_member_id = request.session.get('team_member_id')
                
                try:
                    lead = Lead.objects.get(id=lead_id)
                    team_member = TeamMember.objects.get(id=team_member_id)
                    
                    # Get client IP
                    ip = self.get_client_ip(request)
                    
                    # Create view activity log
                    LeadViewActivity.objects.create(
                        lead=lead,
                        viewed_by=team_member,
                        ip_address=ip
                    )
                except (Lead.DoesNotExist, TeamMember.DoesNotExist):
                    pass
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip