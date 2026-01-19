from django.urls import path
from . import views, sync_views, analytics_views, filtered_analytics

urlpatterns = [
    path('webhook/tata-tele/<int:webhook_id>/', views.TataWebhookView.as_view(), name='tata_webhook'),
    path('lead/<int:lead_id>/calls/', views.get_lead_calls, name='lead_calls'),
    path('initiate-call/', views.initiate_call, name='initiate_call'),
    path('add-note/', views.add_call_note, name='add_call_note'),
    path('calls/', views.calls_dashboard, name='calls_dashboard'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('api/recent-calls/', views.recent_calls_api, name='recent_calls_api'),
    path('api/calls-analytics/', analytics_views.calls_analytics_api, name='calls_analytics'),
    path('api/analytics-filtered/', filtered_analytics.analytics_filtered_api, name='analytics_filtered'),
    path('sync-calls/', views.sync_calls, name='sync_calls'),
    path('sync-status/', views.sync_status, name='sync_status'),
    path('toggle-auto-sync/', views.toggle_auto_sync, name='toggle_auto_sync'),
    path('debug-api/', views.debug_tata_api, name='debug_tata_api'),
    path('sync-all-data/', views.sync_all_tata_data, name='sync_all_tata_data'),
    path('tata-data/', views.tata_data_dashboard, name='tata_data_dashboard'),
    path('export-calls/', views.export_calls, name='export_calls'),
    path('export-leads/', views.export_leads, name='export_leads'),
    path('sync-historical-meta/', views.sync_historical_meta, name='sync_historical_meta'),
    path('sync-all-calls/', analytics_views.sync_all_calls, name='sync_all_calls'),
]