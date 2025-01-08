from django.core.mail import get_connection, EmailMessage
from django.conf import settings
from django.utils import timezone
from .models import EmailTrackingEvent
import uuid

class BulkEmailService:
    def __init__(self, smtp_settings):
        self.smtp_settings = smtp_settings
        self.connection = get_connection(
            host=smtp_settings.host,
            port=smtp_settings.port,
            username=smtp_settings.username,
            password=smtp_settings.password,
            use_tls=smtp_settings.use_tls
        )

    def send_bulk_emails(self, campaign, contacts, template):
        """Send bulk emails with tracking"""
        messages = []
        for contact in contacts:
            tracking_id = str(uuid.uuid4())
            
            # Personalize content
            personalized_content = self._personalize_content(template.content, contact)
            
            # Add tracking pixel and convert links
            tracked_content = self._add_tracking(personalized_content, tracking_id)
            
            # Create email message
            email = EmailMessage(
                subject=template.subject,
                body=tracked_content,
                from_email=self.smtp_settings.username,
                to=[contact.email],
                connection=self.connection,
            )
            email.content_subtype = "html"
            messages.append(email)
            
            # Create tracking event
            EmailTrackingEvent.objects.create(
                campaign=campaign,
                recipient=contact,
                event_type='sent',
                metadata={'tracking_id': tracking_id}
            )
        
        # Send emails in bulk
        return self.connection.send_messages(messages)

    def _personalize_content(self, content, contact):
        """Replace variables in content with contact data"""
        replacements = {
            '{{first_name}}': contact.first_name,
            '{{last_name}}': contact.last_name,
            '{{email}}': contact.email,
            '{{company}}': contact.company or '',
        }
        
        for key, value in replacements.items():
            content = content.replace(key, value)
        return content

    def _add_tracking(self, content, tracking_id):
        """Add tracking pixel and convert links"""
        tracking_pixel = f'<img src="{settings.SITE_URL}/track/open/{tracking_id}/" width="1" height="1" />'
        
        # Add tracking to links
        content = content.replace('href="', f'href="{settings.SITE_URL}/track/click/{tracking_id}/?url=')
        
        return content + tracking_pixel 