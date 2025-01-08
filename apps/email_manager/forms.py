from django import forms
from .models import SMTPSettings  # This should match the model definition

class SMTPConfigurationForm(forms.ModelForm):
    class Meta:
        model = SMTPSettings
        fields = ['host', 'port', 'username', 'password', 'use_tls']  # Adjust fields as necessary 