from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class SMTPSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_manager_smtp_settings')
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)

    def __str__(self):
        return f"SMTP Settings for {self.user.username}"

class EmailLog(models.Model):
    campaign = models.ForeignKey('campaigns.Campaign', on_delete=models.CASCADE)
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('bounced', 'Bounced'),
        ('spam', 'Marked as Spam'),
    ])
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Email to {self.recipient} - {self.status}"