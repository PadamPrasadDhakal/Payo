from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from allauth.socialaccount.signals import pre_social_login
from allauth.socialaccount.models import SocialAccount
from .models import User


@receiver(post_save, sender=User)
def initialize_user_tokens(sender, instance, created, **kwargs):
    """
    Initialize new users with 7 tokens when they first register
    """
    if created:
        # Set initial tokens for new users
        instance.tokens_left = 7
        instance.last_token_reset = timezone.now()
        instance.tokens_restored_flag = False
        instance.save(update_fields=['tokens_left', 'last_token_reset', 'tokens_restored_flag'])


@receiver(pre_social_login)
def handle_google_social_login(sender, **kwargs):
    """Handle Google OAuth login/signup"""
    request = kwargs['request']
    sociallogin = kwargs['sociallogin']
    
    # Only handle Google accounts
    if sociallogin.account.provider == 'google':
        user = sociallogin.user
        
        # If this is a new user (signup), set as applicant
        if not user.pk:
            user.user_type = User.UserType.APPLICANT
            # The user will be saved by allauth after this signal