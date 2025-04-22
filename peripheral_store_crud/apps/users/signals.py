from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.db.models.signals import post_save
from allauth.socialaccount.models import SocialAccount
from .models import Profile

@receiver(user_signed_up)
def create_user_profile(request, user, **kwargs):
    """Create a user profile when a new user signs up via social account"""
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)