from django.urls import path
from .views import SignUpView, home
from .views import CampaignListView, CampaignCreateView, CampaignUpdateView, CampaignDeleteView, EmailTemplateListView, EmailTemplateCreateView, EmailTemplateUpdateView, EmailTemplateDeleteView, ContactListView, ContactCreateView, ContactUpdateView, ContactDeleteView, AnalyticsDashboardView, campaign_analytics_data, export_campaign_report, track_open, track_click, CRMIntegrationView, sync_crm_contacts, twenty_webhook
from . import views

urlpatterns = [
    path('campaigns/', CampaignListView.as_view(), name='campaign_list'),
    path('campaigns/create/', CampaignCreateView.as_view(), name='campaign_create'),
    path('campaigns/<int:pk>/update/', CampaignUpdateView.as_view(), name='campaign_update'),
    path('campaigns/<int:pk>/delete/', CampaignDeleteView.as_view(), name='campaign_delete'),
    path('email-templates/', EmailTemplateListView.as_view(), name='email_template_list'),
    path('email-templates/create/', EmailTemplateCreateView.as_view(), name='email_template_create'),
    path('email-templates/<int:pk>/update/', EmailTemplateUpdateView.as_view(), name='email_template_update'),
    path('email-templates/<int:pk>/delete/', EmailTemplateDeleteView.as_view(), name='email_template_delete'),
    path('contacts/', ContactListView.as_view(), name='contact_list'),
    path('contacts/add/', ContactCreateView.as_view(), name='contact_create'),
    path('contacts/<int:pk>/edit/', ContactUpdateView.as_view(), name='contact_update'),
    path('contacts/<int:pk>/delete/', ContactDeleteView.as_view(), name='contact_delete'),
    path('analytics/', AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('analytics/<int:campaign_id>/data/', campaign_analytics_data, name='campaign_analytics_data'),
    path('analytics/<int:campaign_id>/export/', export_campaign_report, name='export_campaign_report'),
    path('track/open/<uuid:tracking_id>/', track_open, name='track_open'),
    path('track/click/<uuid:tracking_id>/', track_click, name='track_click'),
    path('', home, name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('smtp/create/', views.smtp_settings_create, name='smtp_settings_create'),
    path('campaign/create/', views.campaign_create, name='campaign_create'),
    path('campaign/<int:campaign_id>/test/', views.campaign_test, name='campaign_test'),
    path('crm-integration/', CRMIntegrationView.as_view(), name='crm_integration'),
    path('crm-integration/sync-contacts/', sync_crm_contacts, name='sync_crm_contacts'),
    path('webhooks/twenty/', twenty_webhook, name='twenty_webhook'),
]