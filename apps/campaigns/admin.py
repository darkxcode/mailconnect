from django.contrib import admin
from .models import (
    Campaign, Contact, SMTPSettings, 
    EmailTemplate, EmailCampaign, CustomUser, Prospect, CampaignAnalytics
)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_by', 'created_at', 'last_active')
    list_filter = ('status', 'created_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)

@admin.register(SMTPSettings)
class SMTPSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'host', 'port', 'use_tls')
    list_filter = ('use_tls',)

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_by', 'created_at')
    search_fields = ('name', 'subject', 'content')
    date_hierarchy = 'created_at'

@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'user', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'company_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'company_name')
    ordering = ('-date_joined',)

@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'created_by', 'created_at')
    list_filter = ('created_at', 'company')
    search_fields = ('name', 'email', 'company')
    date_hierarchy = 'created_at'

@admin.register(CampaignAnalytics)
class CampaignAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'campaign',
        'sent_count',
        'opened_count',
        'clicked_count',
        'replied_count',
        'last_updated'
    ]
    date_hierarchy = 'last_updated'
