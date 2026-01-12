from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from leads import activity_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('leads.urls')),
    path('ivr-webhooks/', include('tata_integration.urls')),
    # Activity URLs (backup)
    path('activity-dashboard/', activity_views.activity_dashboard, name='activity_dashboard_backup'),
    path('lead-activity/<int:lead_id>/', activity_views.lead_activity_detail, name='lead_activity_detail_backup'),
    path('reassign-lead/', activity_views.reassign_lead, name='reassign_lead_backup'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)