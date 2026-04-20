from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from profiles.models import MatrimonialProfile, PartnerPreference


@receiver(post_save, sender=User)
def create_profile_and_preferences(sender, instance, created, **kwargs):
    if created:
        MatrimonialProfile.objects.create(user=instance)
        PartnerPreference.objects.create(user=instance)
