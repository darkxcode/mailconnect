from django.urls import path
from . import views

urlpatterns = [
    path('smtp-config/', views.smtp_config, name='smtp_config'),
    path('test-smtp-config/', views.test_smtp_config, name='test_smtp_config'),
]