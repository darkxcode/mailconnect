from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from .utils import add_tracking_to_email
from .services import BulkEmailService
from .models import Campaign, Contact, SMTPSettings, EmailTemplate

@shared_task
def send_campaign_email(campaign_id, recipient_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        recipient = Contact.objects.get(id=recipient_id)
        
        # Add tracking to email content
        tracked_content = add_tracking_to_email(campaign, campaign.content, recipient)
        
        # Send email with tracked content
        send_mail(
            subject=campaign.subject,
            message='',  # Empty plain text version
            html_message=tracked_content,  # HTML version with tracking
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        
        # Update analytics
        analytics = campaign.analytics
        analytics.total_sent += 1
        analytics.total_delivered += 1  # You might want to confirm delivery through bounce handling
        analytics.update_rates()
        
    except Exception as e:
        print(f"Error sending campaign email: {e}")
        # You might want to log this error or update analytics accordingly

@shared_task
def send_bulk_campaign_email(campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        contacts = Contact.objects.all()  # Adjust as necessary

        for contact in contacts:
            # Use the individual send task for each contact to ensure proper tracking
            send_campaign_email.delay(campaign_id, contact.id)
            
    except Exception as e:
        print(f"Error in bulk campaign: {e}")

@shared_task
def process_campaign(campaign_id, batch_size=100):
    """Process campaign emails in batches"""
    campaign = Campaign.objects.get(id=campaign_id)
    smtp_settings = SMTPSettings.objects.get(user=campaign.created_by)
    template = EmailTemplate.objects.get(id=campaign.template_id)
    
    # Get contacts that haven't been processed yet
    contacts = Contact.objects.filter(
        created_by=campaign.created_by,
        campaigncontact__isnull=True
    )[:batch_size]
    
    if contacts:
        email_service = BulkEmailService(smtp_settings)
        email_service.send_bulk_emails(campaign, contacts, template)
        
        # Schedule next batch if there are more contacts
        if contacts.count() == batch_size:
            process_campaign.delay(campaign_id, batch_size)