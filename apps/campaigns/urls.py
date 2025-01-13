from django.urls import path
from . import views

urlpatterns = [
    # Campaign URLs
    path('campaigns/', views.campaign_list, name='campaigns'),
    path('campaigns/create/', views.campaign_create, name='campaign_create'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:pk>/edit/', views.campaign_edit, name='campaign_edit'),
    path('campaigns/<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
    
    # Prospect URLs
    path('prospects/', views.prospect_list, name='prospects'),
    path('prospects/create/', views.prospect_create, name='prospect_create'),
    path('prospects/<int:pk>/edit/', views.prospect_edit, name='prospect_edit'),
    path('prospects/<int:pk>/delete/', views.prospect_delete, name='prospect_delete'),
    
    # Template URLs
    path('templates/', views.template_list, name='templates'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
]