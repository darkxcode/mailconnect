from django.urls import reverse
from django.conf import settings
from urllib.parse import quote
import uuid
from .models import EmailTrackingEvent

def add_tracking_to_email(campaign, email_content, recipient):
    # Generate tracking ID
    tracking_id = uuid.uuid4()
    
    # Add tracking pixel
    pixel_url = f"{settings.SITE_URL}{reverse('track_open', args=[tracking_id])}"
    tracking_pixel = f'<img src="{pixel_url}" width="1" height="1" alt="" style="display:none">'
    
    # Add click tracking to links
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(email_content, 'html.parser')
    
    for link in soup.find_all('a'):
        original_url = link.get('href')
        if original_url and original_url.startswith(('http://', 'https://')):
            tracking_url = f"{settings.SITE_URL}{reverse('track_click', args=[tracking_id])}?url={quote(original_url)}"
            link['href'] = tracking_url
    
    modified_content = str(soup) + tracking_pixel
    
    # Create initial tracking event
    EmailTrackingEvent.objects.create(
        campaign=campaign,
        recipient=recipient,
        event_type='sent',
        metadata={'tracking_id': str(tracking_id)}
    )
    
    return modified_content 