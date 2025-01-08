from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Contact, Campaign, CRMIntegration
import hmac
import hashlib

def verify_webhook_signature(request, secret):
    """Verify Twenty CRM webhook signature"""
    signature = request.headers.get('X-Twenty-Signature')
    if not signature:
        return False
    
    expected = hmac.new(
        secret.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)

@csrf_exempt
@require_POST
def twenty_webhook(request):
    """Handle Twenty CRM webhooks"""
    integration = CRMIntegration.objects.filter(provider='twenty').first()
    if not integration:
        return HttpResponse(status=404)
    
    if not verify_webhook_signature(request, integration.api_key):
        return HttpResponse(status=401)
    
    try:
        payload = json.loads(request.body)
        event_type = payload.get('event')
        
        if event_type == 'contact.created':
            handle_contact_created(payload['data'])
        elif event_type == 'contact.updated':
            handle_contact_updated(payload['data'])
        elif event_type == 'deal.closed':
            handle_deal_closed(payload['data'])
        
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(str(e), status=400)

def handle_contact_created(data):
    """Handle contact creation webhook"""
    Contact.objects.create(
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        company=data.get('company', {}).get('name', '')
    )

def handle_contact_updated(data):
    """Handle contact update webhook"""
    contact = Contact.objects.filter(email=data['email']).first()
    if contact:
        contact.first_name = data.get('first_name', contact.first_name)
        contact.last_name = data.get('last_name', contact.last_name)
        contact.company = data.get('company', {}).get('name', contact.company)
        contact.save()

def handle_deal_closed(data):
    """Handle deal closed webhook"""
    # Add custom logic for when a deal is closed in Twenty
    pass 