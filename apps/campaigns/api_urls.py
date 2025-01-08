from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/', views.CampaignListCreateAPIView.as_view(), name='campaign-list-create'),
    path('campaigns/<int:pk>/', views.CampaignDetailAPIView.as_view(), name='campaign-detail'),
    path('smtp-settings/', views.SMTPSettingsListCreateAPIView.as_view(), name='smtp-settings-list-create'),
    path('campaign-logs/', views.CampaignLogListAPIView.as_view(), name='campaign-log-list'),
] 