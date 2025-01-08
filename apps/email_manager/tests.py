from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import SMTPConfiguration, EmailLog
from apps.campaigns.models import Campaign

User = get_user_model()

class SMTPConfigurationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.smtp_config = SMTPConfiguration.objects.create(
            user=self.user,
            host='smtp.example.com',
            port=587,
            username='smtp_user',
            password='smtp_pass',
            use_tls=True,
            from_email='sender@example.com'
        )

    def test_smtp_configuration_creation(self):
        self.assertTrue(isinstance(self.smtp_config, SMTPConfiguration))
        self.assertEqual(self.smtp_config.__str__(), f"SMTP Config for {self.user.email}")

class EmailLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.campaign = Campaign.objects.create(name='Test Campaign', created_by=self.user)
        self.email_log = EmailLog.objects.create(
            campaign=self.campaign,
            recipient='recipient@example.com',
            subject='Test Subject',
            status='sent'
        )

    def test_email_log_creation(self):
        self.assertTrue(isinstance(self.email_log, EmailLog))
        self.assertEqual(self.email_log.__str__(), f"Email to recipient@example.com - sent")