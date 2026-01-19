from django.contrib import admin
from .models import Lead
from .acefone_models import AcefoneConfig, DIDNumber, CallRecord, ClickApiKey
from .callkaro_models import CallKaroConfig, CallKaroAgent, CallKaroCampaign, CallKaroCallLog
from .booking_models import UnitedNetworkBooking
from .ai_agent_models import AIAgent, AICallLog

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone_number', 'form_name', 'created_time']
    list_filter = ['form_name', 'created_time']
    search_fields = ['full_name', 'email', 'phone_number']
    readonly_fields = ['lead_id', 'synced_at']

@admin.register(DIDNumber)
class DIDNumberAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'number', 'assigned_user', 'is_active']
    list_filter = ['is_active', 'assigned_user']
    search_fields = ['display_name', 'number']

@admin.register(CallRecord)
class CallRecordAdmin(admin.ModelAdmin):
    list_display = ['acefone_call_id', 'lead_name', 'agent', 'status', 'duration', 'started_at']
    list_filter = ['status', 'started_at']
    search_fields = ['acefone_call_id', 'lead_name', 'lead_number']
    readonly_fields = ['acefone_call_id', 'started_at', 'ended_at', 'created_at']

@admin.register(ClickApiKey)
class ClickApiKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'agent', 'enabled', 'created_at']
    list_filter = ['enabled', 'created_at']
    search_fields = ['name', 'agent__name']
    readonly_fields = ['created_at']

@admin.register(AcefoneConfig)
class AcefoneConfigAdmin(admin.ModelAdmin):
    list_display = ['base_url', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UnitedNetworkBooking)
class UnitedNetworkBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'customer_name', 'project_name', 'formatted_amount', 'status', 'created_at']
    list_filter = ['status', 'project_name', 'created_at', 'received_at']
    search_fields = ['booking_id', 'customer_name', 'customer_phone', 'project_name']
    readonly_fields = ['booking_id', 'api_key', 'created_at', 'received_at', 'raw_payload']
    
    fieldsets = (
        ('Booking Info', {
            'fields': ('booking_id', 'api_key', 'status', 'booking_source')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'customer_address', 'nominee_name')
        }),
        ('Unit Details', {
            'fields': ('unit_type', 'unit_number', 'area', 'total_amount', 'booking_amount')
        }),
        ('Project Info', {
            'fields': ('project_name', 'project_location', 'developer')
        }),
        ('Channel Partner', {
            'fields': ('cp_code', 'cp_company', 'cp_name', 'cp_phone', 'cp_email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'received_at')
        }),
        ('Raw Data', {
            'fields': ('raw_payload',),
            'classes': ('collapse',)
        })
    )

@admin.register(CallKaroConfig)
class CallKaroConfigAdmin(admin.ModelAdmin):
    list_display = ['default_agent_id', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Configuration', {
            'fields': ('api_key', 'default_agent_id', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )

@admin.register(CallKaroAgent)
class CallKaroAgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'agent_id', 'assigned_team_member', 'is_active', 'created_at']
    list_filter = ['is_active', 'assigned_team_member', 'created_at']
    search_fields = ['name', 'agent_id', 'description']
    readonly_fields = ['created_at']

@admin.register(CallKaroCampaign)
class CallKaroCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'batch_id', 'agent', 'created_by', 'total_calls', 'completed_calls', 'status', 'created_at']
    list_filter = ['status', 'agent', 'created_by', 'created_at']
    search_fields = ['name', 'batch_id']
    readonly_fields = ['batch_id', 'created_at']

@admin.register(CallKaroCallLog)
class CallKaroCallLogAdmin(admin.ModelAdmin):
    list_display = ['call_id', 'phone_number', 'agent', 'campaign', 'initiated_by', 'status', 'duration_formatted', 'created_at']
    list_filter = ['status', 'agent', 'campaign', 'initiated_by', 'created_at']
    search_fields = ['call_id', 'phone_number', 'lead__full_name']
    readonly_fields = ['call_id', 'created_at', 'started_at', 'ended_at']
    
    fieldsets = (
        ('Call Info', {
            'fields': ('call_id', 'phone_number', 'lead', 'status', 'duration')
        }),
        ('Agent & Campaign', {
            'fields': ('agent', 'campaign', 'initiated_by')
        }),
        ('Scheduling', {
            'fields': ('scheduled_at', 'min_trigger_time', 'max_trigger_time', 'carry_over', 'number_of_retries', 'gap_between_retries', 'priority')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'ended_at')
        })
    )

@admin.register(AIAgent)
class AIAgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'agent_id', 'project', 'is_active', 'created_at']
    list_filter = ['is_active', 'project', 'created_at']
    search_fields = ['name', 'agent_id', 'project__name']
    readonly_fields = ['created_at']

@admin.register(AICallLog)
class AICallLogAdmin(admin.ModelAdmin):
    list_display = ['lead', 'phone_number', 'agent', 'status', 'initiated_at']
    list_filter = ['status', 'agent', 'initiated_at']
    search_fields = ['lead__full_name', 'phone_number', 'call_id']
    readonly_fields = ['initiated_at', 'completed_at']
    
    fieldsets = (
        ('Call Info', {
            'fields': ('lead', 'phone_number', 'agent', 'status', 'call_id')
        }),
        ('Timestamps', {
            'fields': ('initiated_at', 'completed_at')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )