from django.contrib import admin
from .models import (
    Campaign, 
    Contact, 
    SMTPSettings, 
    EmailTemplate, 
    CampaignContact,
    CampaignAnalytics,
    EmailTrackingEvent,
    CustomUser,
    Prospect
)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_by', 'created_at', 'last_active')
    list_filter = ('status', 'created_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('created_at',)

@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'created_by', 'created_at')
    search_fields = ('name', 'email', 'company')
    list_filter = ('created_at',)

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject')
    search_fields = ('name', 'subject', 'body')

@admin.register(SMTPSettings)
class SMTPSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'host', 'port', 'use_tls')
    list_filter = ('use_tls',)

@admin.register(CampaignContact)
class CampaignContactAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'contact', 'sent_at', 'opened_at', 'clicked_at')
    list_filter = ('sent_at', 'opened_at', 'clicked_at')
    search_fields = ('campaign__name', 'contact__email')

@admin.register(CampaignAnalytics)
class CampaignAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'total_sent', 'total_opened', 'total_clicked', 'total_replied')
    list_filter = ('last_updated',)
    search_fields = ('campaign__name',)

@admin.register(EmailTrackingEvent)
class EmailTrackingEventAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'recipient', 'event_type', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('campaign__name', 'recipient__email')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
