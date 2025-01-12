from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Campaign, Contact, SMTPSettings, CustomUser, EmailTemplate, EmailCampaign

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    company = forms.CharField(max_length=100, required=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'email', 'company', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Use email as username
        user.company_name = self.cleaned_data['company']
        if commit:
            user.save()
        return user

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class SMTPSettingsForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = SMTPSettings
        fields = ['host', 'port', 'username', 'password', 'use_tls']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Contact.objects.filter(email=email).exists():
            raise forms.ValidationError('A contact with this email already exists.')
        return email

class ContactImportForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a CSV file',
        help_text='File must contain "name" and "email" columns',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

class TestEmailForm(forms.Form):
    recipient = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'rich-text-editor'}),
        }

class EmailCampaignForm(forms.ModelForm):
    class Meta:
        model = EmailCampaign
        fields = ['name', 'subject', 'body', 'smtp_settings']