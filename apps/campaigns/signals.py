from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Campaign, CampaignAnalytics

@receiver(post_save, sender=Campaign)
def create_campaign_analytics(sender, instance, created, **kwargs):
    if created:
        CampaignAnalytics.objects.create(campaign=instance) 