from django.contrib import admin
from .models import SMTPSettings, EmailLog

@admin.register(SMTPSettings)
class SMTPSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'host', 'port', 'username', 'use_tls')
    list_filter = ('use_tls',)
    search_fields = ('user__email', 'host', 'username', 'from_email')

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'recipient', 'subject', 'sent_at', 'status')
    list_filter = ('status', 'sent_at')
    search_fields = ('recipient', 'subject', 'campaign__name')
    date_hierarchy = 'sent_at'