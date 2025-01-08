from django.conf import settings
import requests
import json

class TwentyCRMIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.twenty.com/v1"  # Replace with actual Twenty API URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def sync_contacts(self, contacts):
        """Sync contacts with Twenty CRM"""
        endpoint = f"{self.base_url}/contacts/bulk"
        payload = {
            "contacts": [
                {
                    "email": contact.email,
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "company": contact.company
                } for contact in contacts
            ]
        }
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()

    def sync_campaign_results(self, campaign):
        """Sync campaign results with Twenty CRM"""
        endpoint = f"{self.base_url}/campaigns"
        payload = {
            "campaign_name": campaign.name,
            "stats": {
                "sent": campaign.analytics.total_sent,
                "opened": campaign.analytics.total_opened,
                "clicked": campaign.analytics.total_clicked,
                "responded": campaign.analytics.total_replied
            }
        }
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json() 