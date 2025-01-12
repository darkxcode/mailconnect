from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.campaigns.views import (
    home, signup, smtp_settings, 
    ContactViewSet, CampaignViewSet, 
    dashboard, create_campaign, 
    email_template_editor, contact_management, 
    analytics_dashboard, settings as campaign_settings
)  # Ensure this import is correct
from django.contrib.auth import views as auth_views  # Add this import
from rest_framework.routers import DefaultRouter
from apps.campaigns import views
from apps.campaigns.views import CustomLoginView

router = DefaultRouter()
router.register(r'contacts', ContactViewSet)
router.register(r'campaigns', CampaignViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('campaigns/', include('apps.campaigns.urls')),
    path('email-templates/', include('apps.email_manager.urls')),
    path('contacts/', include('apps.email_manager.urls')),
    path('api/', include(router.urls)),
    path('email/', include('apps.email_manager.urls')),
    path('', home, name='home'),  # Add this line for the home view
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/signup/', signup, name='signup'),
    path('smtp_settings/', smtp_settings, name='smtp_settings'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/dashboard/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('campaigns/', views.campaign_list, name='campaigns'),
    path('prospects/', views.prospect_list, name='prospects'),
    path('templates/', views.template_list, name='templates'),
    path('reports/', views.report_list, name='reports'),
    path('create-campaign/', create_campaign, name='create_campaign'),
    path('email-template-editor/', email_template_editor, name='email_template_editor'),
    path('contact-management/', contact_management, name='contact_management'),
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('settings/', campaign_settings, name='settings'),
    # Password Reset URLs
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html'
         ),
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('prospects/create/', views.prospect_create, name='prospect_create'),
    path('prospects/<int:pk>/edit/', views.prospect_edit, name='prospect_edit'),
    path('prospects/<int:pk>/delete/', views.prospect_delete, name='prospect_delete'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)