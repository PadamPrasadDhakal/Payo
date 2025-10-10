from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse
from .models import User


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_signup_redirect_url(self, request):
        """Redirect Google OAuth users to profile completion if needed"""
        user = request.user
        
        if user.user_type == User.UserType.APPLICANT and not user.official_name:
            return reverse('users:add_info')
        else:
            return reverse('users:dashboard')
    
    def get_login_redirect_url(self, request):
        """Redirect existing Google OAuth users"""
        user = request.user
        
        if user.user_type == User.UserType.APPLICANT and not user.official_name:
            return reverse('users:add_info')
        else:
            return reverse('users:dashboard')