from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from allauth.socialaccount.signals import pre_social_login
from allauth.socialaccount.models import SocialAccount
from .models import User
from .models import IndividualKYC, OrganizationKYC, KycAudit, Notification


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


@receiver(post_save, sender=IndividualKYC)
def individual_kyc_post_save(sender, instance, created, **kwargs):
    # When KYC becomes VERIFIED, update user's flag and create audit + notification
    if instance.status == IndividualKYC.KycStatus.VERIFIED:
        instance.user.is_kyc_verified = True
        instance.user.kyc_last_submitted = instance.submitted_at or None
        instance.user.save(update_fields=['is_kyc_verified', 'kyc_last_submitted'])
        KycAudit.objects.create(kyc_type='IND', kyc_id=instance.id, actor=None, action='VERIFIED', message='Auto-updated via signal')
        # Create notification
        Notification.objects.create(
            user=instance.user,
            title='KYC Verification Approved ✓',
            message='Congratulations! Your KYC verification has been approved. You can now apply for unlimited jobs.',
            notification_type='KYC_VERIFIED',
            related_id=instance.id
        )
    elif instance.status == IndividualKYC.KycStatus.REJECTED:
        instance.user.is_kyc_verified = False
        instance.user.save(update_fields=['is_kyc_verified'])
        KycAudit.objects.create(kyc_type='IND', kyc_id=instance.id, actor=None, action='REJECTED', message='Auto-updated via signal')
        # Create notification
        rejection_msg = instance.rejection_reason if instance.rejection_reason else 'Your KYC was rejected. Please review and resubmit.'
        Notification.objects.create(
            user=instance.user,
            title='KYC Verification Rejected ✗',
            message=f'Your KYC verification was rejected: {rejection_msg}',
            notification_type='KYC_REJECTED',
            related_id=instance.id
        )


@receiver(post_save, sender=OrganizationKYC)
def organization_kyc_post_save(sender, instance, created, **kwargs):
    if instance.status == OrganizationKYC.KycStatus.VERIFIED:
        instance.user.is_kyc_verified = True
        instance.user.kyc_last_submitted = instance.submitted_at or None
        instance.user.save(update_fields=['is_kyc_verified', 'kyc_last_submitted'])
        KycAudit.objects.create(kyc_type='ORG', kyc_id=instance.id, actor=None, action='VERIFIED', message='Auto-updated via signal')
        # Create notification
        Notification.objects.create(
            user=instance.user,
            title='Organization KYC Verification Approved ✓',
            message='Congratulations! Your organization KYC verification has been approved. You can now post jobs.',
            notification_type='KYC_VERIFIED',
            related_id=instance.id
        )
    elif instance.status == OrganizationKYC.KycStatus.REJECTED:
        instance.user.is_kyc_verified = False
        instance.user.save(update_fields=['is_kyc_verified'])
        KycAudit.objects.create(kyc_type='ORG', kyc_id=instance.id, actor=None, action='REJECTED', message='Auto-updated via signal')
        # Create notification
        rejection_msg = instance.rejection_reason if instance.rejection_reason else 'Your organization KYC was rejected. Please review and resubmit.'
        Notification.objects.create(
            user=instance.user,
            title='Organization KYC Verification Rejected ✗',
            message=f'Your organization KYC verification was rejected: {rejection_msg}',
            notification_type='KYC_REJECTED',
            related_id=instance.id
        )
