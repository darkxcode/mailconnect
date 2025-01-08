import csv
import json
import io
import uuid
from urllib.parse import unquote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg
from PIL import Image
from django.utils import timezone
from datetime import timedelta

from .models import (
    Campaign, 
    SMTPSettings, 
    Contact, 
    CampaignContact, 
    EmailTemplate, 
    EmailCampaign, 
    CampaignAnalytics, 
    EmailTrackingEvent,
    Prospect,
    CRMIntegration,
    CRMSyncLog
)
from .forms import (
    CampaignForm, 
    SMTPSettingsForm, 
    TestEmailForm, 
    ContactImportForm, 
    EmailTemplateForm, 
    ContactForm,
    CustomUserCreationForm,
    EmailCampaignForm
)
from .tasks import send_campaign_email
from .serializers import (
    SMTPSettingsSerializer, 
    ContactSerializer, 
    CampaignSerializer, 
    EmailCampaignSerializer
)
from .utils import add_tracking_to_email
from .twenty_integration import TwentyCRMIntegration
from .services import BulkEmailService

User = get_user_model()  # Get the custom user model

# Ensure the signup function is defined here
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# Campaign Views
@login_required
def campaign_list(request):
    campaigns = Campaign.objects.filter(created_by=request.user)
    return render(request, 'campaigns/campaign_list.html', {'campaigns': campaigns})

@login_required
def campaign_create(request):
    if request.method == 'POST':
        form = EmailCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.save()
            messages.success(request, 'Campaign created successfully!')
            return redirect('campaign_test', campaign_id=campaign.id)
    else:
        form = EmailCampaignForm()
    
    return render(request, 'campaigns/campaign_form.html', {'form': form})

@login_required
def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, created_by=request.user)
    form = CampaignForm(request.POST or None, instance=campaign)
    if form.is_valid():
        form.save()
        messages.success(request, 'Campaign updated successfully.')
        return redirect('campaign_list')
    return render(request, 'campaigns/campaign_form.html', {'form': form, 'campaign': campaign})

@login_required
def campaign_send(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, created_by=request.user)
    contacts = Contact.objects.all()  # In a real-world scenario, you might want to filter this

    for contact in contacts:
        # Logic to send the campaign email to the contact
        send_campaign_email.delay(campaign.id, contact.id)

    messages.success(request, f"Campaign '{campaign.name}' is being sent.")
    return redirect('campaign_list')  # Redirect to the campaign list after sending

# SMTP Settings Views
@login_required
def smtp_settings(request):
    settings_instance = SMTPSettings.objects.filter(user=request.user).first()
    form = SMTPSettingsForm(request.POST or None, instance=settings_instance)
    if form.is_valid():
        settings_instance = form.save(commit=False)
        settings_instance.user = request.user
        settings_instance.save()
        messages.success(request, 'SMTP settings updated successfully.')
        return redirect('smtp_settings')  # Redirect to the same page after saving
    return render(request, 'smtp_settings.html', {'form': form})

@login_required
def smtp_settings_create(request):
    if request.method == 'POST':
        form = SMTPSettingsForm(request.POST)
        if form.is_valid():
            smtp_settings = form.save(commit=False)
            smtp_settings.user = request.user
            smtp_settings.save()
            messages.success(request, 'SMTP settings saved successfully!')
            return redirect('campaign_create')
    else:
        form = SMTPSettingsForm()
    
    return render(request, 'campaigns/smtp_settings_form.html', {'form': form})

# Test Email View
def send_test_email(request):
    form = TestEmailForm(request.POST or None)
    if form.is_valid():
        recipient = form.cleaned_data['recipient']
        subject = "Test Email from MailConnect"
        message = "This is a test email sent from your MailConnect application."
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient],
                fail_silently=False,
            )
            messages.success(request, f"Test email sent successfully to {recipient}")
        except Exception as e:
            messages.error(request, f"Failed to send test email. Error: {str(e)}")
        return redirect('send_test_email')
    return render(request, 'campaigns/send_test_email.html', {'form': form})

# Contact Import/Export Views
@login_required
def import_contacts(request):
    if request.method == 'POST':
        form = ContactImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                Contact.objects.get_or_create(email=row['email'], defaults={'name': row.get('name', '')})
            messages.success(request, 'Contacts imported successfully.')
            return redirect('contact_list')
    else:
        form = ContactImportForm()
    return render(request, 'campaigns/import_contacts.html', {'form': form})

@login_required
def export_contacts(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
    writer = csv.writer(response)
    writer.writerow(['Email', 'Name'])
    contacts = Contact.objects.all().values_list('email', 'name')
    for contact in contacts:
        writer.writerow(contact)
    return response

@login_required
def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'campaigns/contact_list.html', {'contacts': contacts})

@login_required
def campaign_analytics(request, pk):
    campaign = Campaign.objects.get(pk=pk)
    analytics = CampaignContact.objects.filter(campaign=campaign)
    context = {
        'campaign': campaign,
        'analytics': analytics,
    }
    return render(request, 'campaigns/campaign_analytics.html', context)

@require_POST
@login_required
def update_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    data = json.loads(request.body)
    contact.email = data.get('email', contact.email)
    contact.name = data.get('name', contact.name)
    contact.save()
    return JsonResponse({'success': True})

@require_POST
@login_required
def delete_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    return JsonResponse({'success': True})

class SignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('dashboard')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return render(request, 'registration/signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return self.render_to_response(self.get_context_data(form=form))

@login_required
def profile(request):
    return render(request, 'registration/profile.html')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = 'campaigns/campaign_list.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
        # Ensure the user is authenticated
        if self.request.user.is_authenticated:
            return Campaign.objects.filter(created_by=self.request.user)
        else:
            return Campaign.objects.none()  # Return an empty queryset if not authenticated

class CampaignCreateView(CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/campaign_form.html'
    success_url = reverse_lazy('campaign_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class CampaignUpdateView(UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/campaign_form.html'
    success_url = reverse_lazy('campaign_list')

    def get_queryset(self):
        return Campaign.objects.filter(created_by=self.request.user)

class CampaignDeleteView(DeleteView):
    model = Campaign
    template_name = 'campaigns/campaign_confirm_delete.html'
    success_url = reverse_lazy('campaign_list')

    def get_queryset(self):
        return Campaign.objects.filter(created_by=self.request.user)

class EmailTemplateListView(ListView):
    model = EmailTemplate
    template_name = 'campaigns/email_template_list.html'
    context_object_name = 'email_templates'

class EmailTemplateCreateView(CreateView):
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'campaigns/email_template_form.html'
    success_url = reverse_lazy('email_template_list')

    def form_valid(self, form):
        return super().form_valid(form)

class EmailTemplateUpdateView(UpdateView):
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'campaigns/email_template_form.html'
    success_url = reverse_lazy('email_template_list')

    def get_queryset(self):
        return EmailTemplate.objects.filter(created_by=self.request.user)

class EmailTemplateDeleteView(DeleteView):
    model = EmailTemplate
    template_name = 'campaigns/email_template_confirm_delete.html'
    success_url = reverse_lazy('email_template_list')

    def get_queryset(self):
        return EmailTemplate.objects.filter(created_by=self.request.user)

class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'campaigns/contact_list.html'
    context_object_name = 'contacts'
    ordering = ['-created_at']

    def get_queryset(self):
        return Contact.objects.filter(created_by=self.request.user)

class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'campaigns/contact_form.html'
    success_url = reverse_lazy('contact_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'campaigns/contact_form.html'
    success_url = reverse_lazy('contact_list')

    def get_queryset(self):
        return Contact.objects.filter(created_by=self.request.user)

class ContactDeleteView(DeleteView):
    model = Contact
    template_name = 'campaigns/contact_confirm_delete.html'
    success_url = reverse_lazy('contact_list')

    def get_queryset(self):
        return Contact.objects.filter(created_by=self.request.user)

class EmailCampaignViewSet(viewsets.ModelViewSet):
    queryset = EmailCampaign.objects.all()
    serializer_class = EmailCampaignSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class SMTPSettingsViewSet(viewsets.ModelViewSet):
    queryset = SMTPSettings.objects.all()
    serializer_class = SMTPSettingsSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def home(request):
    return render(request, 'home.html')

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

@login_required
def dashboard(request):
    # Get user's campaign statistics
    active_campaigns = Campaign.objects.filter(
        created_by=request.user,
        status='active'
    )
    
    context = {
        'active_campaigns_count': active_campaigns.count(),
        'total_prospects': Prospect.objects.filter(created_by=request.user).count(),
        'open_rate': Campaign.objects.filter(created_by=request.user).aggregate(Avg('open_rate'))['open_rate__avg'] or 0,
        'response_rate': Campaign.objects.filter(created_by=request.user).aggregate(Avg('response_rate'))['response_rate__avg'] or 0,
        'recent_campaigns': Campaign.objects.filter(created_by=request.user).order_by('-last_active')[:5]
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def dashboard_stats_api(request):
    """API endpoint for dashboard statistics"""
    stats = {
        'active_campaigns': Campaign.objects.filter(created_by=request.user, status='active').count(),
        'total_prospects': Prospect.objects.filter(created_by=request.user).count(),
        'open_rate': Campaign.objects.filter(created_by=request.user).aggregate(Avg('open_rate'))['open_rate__avg'] or 0,
        'response_rate': Campaign.objects.filter(created_by=request.user).aggregate(Avg('response_rate'))['response_rate__avg'] or 0,
    }
    return JsonResponse(stats)

def create_campaign(request):
    return render(request, 'campaign_creation.html')

def email_template_editor(request):
    return render(request, 'email_template_editor.html')

def contact_management(request):
    return render(request, 'contact_management.html')

def analytics_dashboard(request):
    return render(request, 'analytics_dashboard.html')

def settings(request):
    return render(request, 'settings.html')

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'campaigns/analytics_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Get user's campaigns
        campaigns = Campaign.objects.filter(created_by=self.request.user)
        
        # Basic stats
        context.update({
            'total_campaigns': campaigns.count(),
            'active_campaigns': campaigns.filter(status='active').count(),
            'total_prospects': Prospect.objects.filter(created_by=self.request.user).count(),
            'campaigns_this_month': campaigns.filter(created_at__gte=start_date).count(),
        })
        
        # Email performance metrics
        tracking_events = EmailTrackingEvent.objects.filter(
            campaign__created_by=self.request.user,
            timestamp__range=[start_date, end_date]
        )
        
        # Detailed email stats
        context['email_stats'] = {
            'sent': tracking_events.filter(event_type='sent').count(),
            'delivered': tracking_events.filter(event_type='delivered').count(),
            'opened': tracking_events.filter(event_type='opened').count(),
            'clicked': tracking_events.filter(event_type='clicked').count(),
            'bounced': tracking_events.filter(event_type='bounced').count(),
            'spam': tracking_events.filter(event_type='spam').count(),
        }
        
        # Calculate rates
        total_sent = context['email_stats']['sent']
        if total_sent > 0:
            context['rates'] = {
                'delivery_rate': (context['email_stats']['delivered'] / total_sent) * 100,
                'open_rate': (context['email_stats']['opened'] / total_sent) * 100,
                'click_rate': (context['email_stats']['clicked'] / total_sent) * 100,
                'bounce_rate': (context['email_stats']['bounced'] / total_sent) * 100,
                'spam_rate': (context['email_stats']['spam'] / total_sent) * 100,
            }
        
        # Time-based analysis
        context['daily_stats'] = self._get_daily_stats(tracking_events, start_date, end_date)
        context['best_times'] = self._get_best_sending_times(tracking_events)
        
        return context

    def _get_daily_stats(self, events, start_date, end_date):
        """Get daily statistics for the date range"""
        daily_stats = {}
        current = start_date
        while current <= end_date:
            day_events = events.filter(timestamp__date=current.date())
            daily_stats[current.strftime('%Y-%m-%d')] = {
                'sent': day_events.filter(event_type='sent').count(),
                'opened': day_events.filter(event_type='opened').count(),
                'clicked': day_events.filter(event_type='clicked').count(),
            }
            current += timedelta(days=1)
        return daily_stats

    def _get_best_sending_times(self, events):
        """Analyze best performing sending times"""
        opened_events = events.filter(event_type='opened')
        return (
            opened_events.annotate(hour=ExtractHour('timestamp'))
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

@login_required
def campaign_analytics_data(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, created_by=request.user)
    analytics = campaign.analytics
    
    # Get time-series data for charts
    events_by_date = EmailTrackingEvent.objects.filter(
        campaign=campaign
    ).values('event_type', 'timestamp__date').annotate(
        count=Count('id')
    ).order_by('timestamp__date')
    
    return JsonResponse({
        'summary': {
            'total_sent': analytics.total_sent,
            'total_opened': analytics.total_opened,
            'total_clicked': analytics.total_clicked,
            'bounce_rate': analytics.bounce_rate,
            'open_rate': analytics.open_rate,
            'click_rate': analytics.click_rate,
        },
        'timeline_data': list(events_by_date)
    })

@login_required
def export_campaign_report(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, created_by=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{campaign.name}_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Email', 'Status', 'Sent At', 'Opened At', 'Clicked At'])
    
    events = EmailTrackingEvent.objects.filter(campaign=campaign).order_by('recipient', 'timestamp')
    
    for event in events:
        writer.writerow([
            event.recipient.email,
            event.event_type,
            event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    return response

@require_GET
def track_open(request, tracking_id):
    try:
        # Create a 1x1 transparent pixel
        img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        
        # Find the tracking event by tracking_id
        tracking_event = EmailTrackingEvent.objects.filter(
            metadata__tracking_id=str(tracking_id)
        ).first()
        
        if tracking_event:
            # Record the open event
            EmailTrackingEvent.objects.create(
                campaign=tracking_event.campaign,
                recipient=tracking_event.recipient,
                event_type='opened',
                metadata={'ip': request.META.get('REMOTE_ADDR')}
            )
            
            # Update analytics
            analytics = tracking_event.campaign.analytics
            analytics.total_opened += 1
            analytics.update_rates()
        
        return response
    except Exception as e:
        print(f"Error tracking open: {e}")
        return HttpResponse(status=200)

@require_GET
def track_click(request, tracking_id):
    try:
        original_url = unquote(request.GET.get('url', ''))
        
        # Find the tracking event by tracking_id
        tracking_event = EmailTrackingEvent.objects.filter(
            metadata__tracking_id=str(tracking_id)
        ).first()
        
        if tracking_event:
            # Record the click event
            EmailTrackingEvent.objects.create(
                campaign=tracking_event.campaign,
                recipient=tracking_event.recipient,
                event_type='clicked',
                metadata={
                    'url': original_url,
                    'ip': request.META.get('REMOTE_ADDR')
                }
            )
            
            # Update analytics
            analytics = tracking_event.campaign.analytics
            analytics.total_clicked += 1
            analytics.update_rates()
        
        return redirect(original_url)
    except Exception as e:
        print(f"Error tracking click: {e}")
        return redirect(original_url)

@login_required
def prospect_list(request):
    prospects = Prospect.objects.filter(created_by=request.user)
    return render(request, 'campaigns/prospect_list.html', {'prospects': prospects})

@login_required
def template_list(request):
    templates = EmailTemplate.objects.filter(created_by=request.user)
    return render(request, 'campaigns/template_list.html', {'templates': templates})

@login_required
def report_list(request):
    campaigns = Campaign.objects.filter(created_by=request.user)
    return render(request, 'campaigns/report_list.html', {'campaigns': campaigns})

@login_required
def prospect_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            prospect = form.save(commit=False)
            prospect.created_by = request.user
            prospect.save()
            return redirect('prospect_list')
    else:
        form = ContactForm()
    return render(request, 'campaigns/prospect_form.html', {'form': form})

@login_required
def prospect_edit(request, pk):
    prospect = get_object_or_404(Prospect, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=prospect)
        if form.is_valid():
            form.save()
            return redirect('prospect_list')
    else:
        form = ContactForm(instance=prospect)
    return render(request, 'campaigns/prospect_form.html', {'form': form})

@login_required
def prospect_delete(request, pk):
    prospect = get_object_or_404(Prospect, pk=pk, created_by=request.user)
    if request.method == 'POST':
        prospect.delete()
        return redirect('prospect_list')
    return render(request, 'campaigns/prospect_confirm_delete.html', {'prospect': prospect})

@login_required
def template_create(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            return redirect('template_list')
    else:
        form = EmailTemplateForm()
    return render(request, 'campaigns/template_form.html', {'form': form})

@login_required
def template_edit(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return redirect('template_list')
    else:
        form = EmailTemplateForm(instance=template)
    return render(request, 'campaigns/template_form.html', {'form': form})

@login_required
def template_delete(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        template.delete()
        return redirect('template_list')
    return render(request, 'campaigns/template_confirm_delete.html', {'template': template})

@login_required
def campaign_test(request, campaign_id):
    campaign = EmailCampaign.objects.get(id=campaign_id)
    
    if request.method == 'POST':
        test_email = request.POST.get('test_email')
        try:
            # Send test email using campaign settings
            send_mail(
                subject=campaign.subject,
                message=campaign.body,
                from_email=campaign.smtp_settings.username,
                recipient_list=[test_email],
                auth_user=campaign.smtp_settings.username,
                auth_password=campaign.smtp_settings.password,
                fail_silently=False,
            )
            messages.success(request, f'Test email sent successfully to {test_email}!')
        except Exception as e:
            messages.error(request, f'Error sending test email: {str(e)}')
    
    return render(request, 'campaigns/campaign_test.html', {'campaign': campaign})

class CRMIntegrationView(LoginRequiredMixin, View):
    template_name = 'campaigns/crm_integration.html'

    def get(self, request):
        integration = CRMIntegration.objects.filter(user=request.user).first()
        sync_logs = CRMSyncLog.objects.filter(
            integration__user=request.user
        ).order_by('-created_at')[:10]
        
        return render(request, self.template_name, {
            'integration': integration,
            'sync_logs': sync_logs
        })

    def post(self, request):
        api_key = request.POST.get('api_key')
        provider = request.POST.get('provider')
        
        integration, created = CRMIntegration.objects.update_or_create(
            user=request.user,
            provider=provider,
            defaults={'api_key': api_key}
        )
        
        messages.success(request, 'CRM integration updated successfully!')
        return redirect('crm_integration')

@login_required
def sync_crm_contacts(request):
    integration = get_object_or_404(CRMIntegration, user=request.user)
    crm = TwentyCRMIntegration(integration.api_key)
    
    try:
        contacts = Contact.objects.filter(created_by=request.user)
        result = crm.sync_contacts(contacts)
        
        CRMSyncLog.objects.create(
            integration=integration,
            sync_type='contacts',
            status='success',
            message=f"Synced {len(contacts)} contacts"
        )
        
        messages.success(request, f"Successfully synced {len(contacts)} contacts!")
    except Exception as e:
        CRMSyncLog.objects.create(
            integration=integration,
            sync_type='contacts',
            status='failed',
            message=str(e)
        )
        messages.error(request, f"Failed to sync contacts: {str(e)}")
    
    return redirect('crm_integration')

@login_required
def send_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, created_by=request.user)
    smtp_settings = get_object_or_404(SMTPSettings, user=request.user)
    
    # Get contacts for campaign
    contacts = Contact.objects.filter(created_by=request.user)
    
    # Get email template
    template = get_object_or_404(EmailTemplate, id=campaign.template_id)
    
    try:
        # Initialize bulk email service
        email_service = BulkEmailService(smtp_settings)
        
        # Send emails
        sent_count = email_service.send_bulk_emails(campaign, contacts, template)
        
        messages.success(request, f'Successfully sent {sent_count} emails!')
        
        # Update campaign status
        campaign.status = 'active'
        campaign.save()
        
        # Sync with CRM if integration exists
        integration = CRMIntegration.objects.filter(user=request.user).first()
        if integration:
            crm = TwentyCRMIntegration(integration.api_key)
            crm.sync_campaign_results(campaign)
        
    except Exception as e:
        messages.error(request, f'Error sending campaign: {str(e)}')
    
    return redirect('campaign_detail', campaign_id=campaign_id)

# Add more views as needed for API endpoints