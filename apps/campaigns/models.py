# apps/campaigns/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Explicitly declare fields from AbstractUser to ensure they're created
    is_superuser = models.BooleanField(
        'superuser status',
        default=False,
        help_text='Designates that this user has all permissions without explicitly assigning them.'
    )
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.'
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active.'
    )
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    last_login = models.DateTimeField('last login', blank=True, null=True)

    class Meta:
        db_table = 'campaigns_customuser'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

# Import get_user_model here
from django.contrib.auth import get_user_model
User = get_user_model()

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        ordering = ['-created_at']

class EmailTemplate(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    body = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Campaign(models.Model):
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed')
    ], default='draft')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campaigns'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    prospects_count = models.IntegerField(default=0)
    open_rate = models.FloatField(default=0)
    response_rate = models.FloatField(default=0)

    def __str__(self):
        return self.name

    @property
    def status_color(self):
        return {
            'draft': 'secondary',
            'active': 'success',
            'paused': 'warning',
            'completed': 'info'
        }.get(self.status, 'secondary')

    class Meta:
        ordering = ['-created_at']

class Prospect(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prospects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['email', 'created_by']

class CampaignAnalytics(models.Model):
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name='analytics')
    sent_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    replied_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def update_rates(self):
        if self.sent_count > 0:
            self.campaign.open_rate = (self.opened_count / self.sent_count) * 100
            self.campaign.response_rate = (self.replied_count / self.sent_count) * 100
            self.campaign.save()

    def __str__(self):
        return f"Analytics for {self.campaign.name}"

class CampaignContact(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('campaign', 'contact')

class SMTPSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SMTP Settings for {self.user.username}"

class EmailCampaign(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    smtp_settings = models.ForeignKey(SMTPSettings, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    opened = models.BooleanField(default=False)
    responded = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class CampaignLog(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
    )

    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE)
    recipient = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('campaign', 'recipient')

class EmailTrackingEvent(models.Model):
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    recipient = models.ForeignKey('Contact', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('bounced', 'Bounced'),
        ('spam', 'Marked as Spam')
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

class CRMIntegration(models.Model):
    PROVIDER_CHOICES = [
        ('twenty', 'Twenty CRM'),
        ('other', 'Other CRM')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=255)
    webhook_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'provider']

class CRMSyncLog(models.Model):
    integration = models.ForeignKey(CRMIntegration, on_delete=models.CASCADE)
    sync_type = models.CharField(max_length=50)  # contacts, campaigns, etc.
    status = models.CharField(max_length=20)  # success, failed
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
