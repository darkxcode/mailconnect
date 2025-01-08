from rest_framework import serializers
from .models import EmailCampaign, SMTPSettings, CampaignLog, Contact, Campaign
from django.contrib.auth import get_user_model

class SMTPSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPSettings
        fields = ['id', 'host', 'port', 'username', 'use_tls']
        extra_kwargs = {'password': {'write_only': True}}

class EmailCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailCampaign
        fields = ['id', 'name', 'subject', 'body', 'status', 'scheduled_time']

class CampaignLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignLog
        fields = ['id', 'campaign', 'recipient', 'status', 'sent_at']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'email', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            'id', 
            'name', 
            'status', 
            'created_by', 
            'created_at', 
            'last_active',
            'prospects_count',
            'open_rate',
            'response_rate'
        ]
        read_only_fields = ['created_at', 'last_active', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'company_name')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user

# Add more serializers as needed for other models 