from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Campaign, Contact, SMTPSettings, CustomUser, EmailTemplate, EmailCampaign

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        error_messages={
            'required': 'First name is required',
            'max_length': 'First name must be less than 30 characters'
        }
    )
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required',
            'invalid': 'Please enter a valid email address'
        }
    )
    company = forms.CharField(
        max_length=100, 
        required=True,
        error_messages={
            'required': 'Company name is required',
            'max_length': 'Company name must be less than 100 characters'
        }
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'email', 'company', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'The two password fields must match.')

        return cleaned_data

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
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter campaign name'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
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

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'email', 'company_name', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }