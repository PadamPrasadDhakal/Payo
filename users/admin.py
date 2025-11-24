from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "user_type",
                    "organization_name",
                    "organization_website",
                    "resume",
                    "skills",
                    "experience",
                )
            },
        ),
        (
            "CMS / Staff Access (Superuser Only)",
            {
                "fields": ("is_staff", "is_superuser", "groups", "user_permissions"),
                "classes": ("collapse",),
                "description": "⚠️ Only superusers can grant CMS access. Mark 'is_staff' to enable CMS admin access."
            },
        ),
    )
    list_display = ("username", "email", "user_type", "is_staff_badge", "is_active")
    
    def is_staff_badge(self, obj):
        """Display staff status with visual indicator"""
        if obj.is_staff:
            return '🔐 CMS Access'
        return '—'
    is_staff_badge.short_description = 'CMS Status'
    
    def get_fieldsets(self, request, obj=None):
        """Hide CMS fieldset from non-superusers"""
        fieldsets = super().get_fieldsets(request, obj)
        
        # If user is not superuser, hide the CMS fieldset
        if not request.user.is_superuser:
            fieldsets = tuple([fs for fs in fieldsets if fs[0] != "CMS / Staff Access (Superuser Only)"])
        
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        """Hide is_staff field from non-superusers"""
        form = super().get_form(request, obj, **kwargs)
        
        if not request.user.is_superuser:
            # Hide staff-related fields for non-superusers
            if 'is_staff' in form.base_fields:
                del form.base_fields['is_staff']
            if 'is_superuser' in form.base_fields:
                del form.base_fields['is_superuser']
            if 'groups' in form.base_fields:
                del form.base_fields['groups']
            if 'user_permissions' in form.base_fields:
                del form.base_fields['user_permissions']
        
        return form
    
    def has_add_permission(self, request):
        """Only superusers can add users"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete users"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Superusers can change all users, staff can only view"""
        if request.user.is_superuser:
            return True
        return request.user.is_staff  # Staff can at least view
    
    actions = ['make_cms_user', 'remove_cms_user']
    
    def make_cms_user(self, request, queryset):
        """Action to grant CMS access - only for superusers"""
        if not request.user.is_superuser:
            self.message_user(request, '❌ Only superusers can grant CMS access.', level='error')
            return
        
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'✓ {updated} user(s) now have CMS access.')
    make_cms_user.short_description = '🔐 Grant CMS Access (Superuser Only)'
    
    def remove_cms_user(self, request, queryset):
        """Action to revoke CMS access - only for superusers"""
        if not request.user.is_superuser:
            self.message_user(request, '❌ Only superusers can revoke CMS access.', level='error')
            return
        
        updated = queryset.update(is_staff=False)
        self.message_user(request, f'✓ {updated} user(s) CMS access removed.')
    remove_cms_user.short_description = '🚫 Revoke CMS Access (Superuser Only)'

from django.contrib import admin
from .models import IndividualKYC, OrganizationKYC, KycAudit


@admin.register(IndividualKYC)
class IndividualKYCAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "submitted_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "full_name", "citizenship_number")
    actions = ["mark_verified", "mark_rejected", "request_more_info"]

    def mark_verified(self, request, queryset):
        for k in queryset:
            k.status = 'VERIFIED'
            k.submitted_at = k.submitted_at or None
            k.save()
            # Update user flag
            k.user.is_kyc_verified = True
            k.user.save(update_fields=['is_kyc_verified'])
            KycAudit.objects.create(kyc_type='IND', kyc_id=k.id, actor=request.user, action='VERIFIED', message='Marked verified via admin action')
    mark_verified.short_description = "Mark selected as VERIFIED"

    def mark_rejected(self, request, queryset):
        for k in queryset:
            k.status = 'REJECTED'
            k.rejection_reason = 'Rejected via admin bulk action'
            k.save()
            k.user.is_kyc_verified = False
            k.user.save(update_fields=['is_kyc_verified'])
            KycAudit.objects.create(kyc_type='IND', kyc_id=k.id, actor=request.user, action='REJECTED', message='Rejected via admin bulk action')
    mark_rejected.short_description = "Mark selected as REJECTED"

    def request_more_info(self, request, queryset):
        for k in queryset:
            k.status = 'DRAFT'
            k.save()
            KycAudit.objects.create(kyc_type='IND', kyc_id=k.id, actor=request.user, action='REQUEST_MORE_INFO', message='Requested more info via admin')
    request_more_info.short_description = "Request more info (move to DRAFT)"


@admin.register(OrganizationKYC)
class OrganizationKYCAdmin(admin.ModelAdmin):
    list_display = ("user", "org_name", "status", "submitted_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "org_name", "registration_number")
    actions = ["mark_verified", "mark_rejected", "request_more_info"]

    def mark_verified(self, request, queryset):
        for k in queryset:
            k.status = 'VERIFIED'
            k.save()
            k.user.is_kyc_verified = True
            k.user.save(update_fields=['is_kyc_verified'])
            KycAudit.objects.create(kyc_type='ORG', kyc_id=k.id, actor=request.user, action='VERIFIED', message='Marked verified via admin action')
    mark_verified.short_description = "Mark selected as VERIFIED"

    def mark_rejected(self, request, queryset):
        for k in queryset:
            k.status = 'REJECTED'
            k.rejection_reason = 'Rejected via admin bulk action'
            k.save()
            k.user.is_kyc_verified = False
            k.user.save(update_fields=['is_kyc_verified'])
            KycAudit.objects.create(kyc_type='ORG', kyc_id=k.id, actor=request.user, action='REJECTED', message='Rejected via admin bulk action')
    mark_rejected.short_description = "Mark selected as REJECTED"

    def request_more_info(self, request, queryset):
        for k in queryset:
            k.status = 'DRAFT'
            k.save()
            KycAudit.objects.create(kyc_type='ORG', kyc_id=k.id, actor=request.user, action='REQUEST_MORE_INFO', message='Requested more info via admin')
    request_more_info.short_description = "Request more info (move to DRAFT)"


@admin.register(KycAudit)
class KycAuditAdmin(admin.ModelAdmin):
    list_display = ("kyc_type", "kyc_id", "actor", "action", "created_at")
    search_fields = ("actor__username", "action", "message")
