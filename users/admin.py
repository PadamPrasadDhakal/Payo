from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Build custom fieldsets to add Profile section
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Profile", {
            "fields": (
                "user_type",
                "organization_name",
                "organization_website",
                "resume",
                "skills",
                "experience",
            )
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "classes": ("collapse",),
            "description": "⚠️ Only superusers can grant CMS access. Mark 'is_staff' to enable CMS admin access."
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
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
        fieldsets = list(super().get_fieldsets(request, obj))
        
        # If user is not superuser, remove staff fields from Permissions fieldset
        if not request.user.is_superuser:
            for i, (name, options) in enumerate(fieldsets):
                if name == "Permissions":
                    # Remove is_staff, is_superuser, groups, user_permissions from non-superusers
                    fields = list(options.get("fields", ()))
                    fields = [f for f in fields if f not in ["is_staff", "is_superuser", "groups", "user_permissions"]]
                    fieldsets[i] = (name, {**options, "fields": tuple(fields)})
        
        return tuple(fieldsets)
    
    def get_form(self, request, obj=None, **kwargs):
        """Hide is_staff field from non-superusers"""
        form = super().get_form(request, obj, **kwargs)
        
        if not request.user.is_superuser:
            # Hide staff-related fields for non-superusers
            for field in ['is_staff', 'is_superuser', 'groups', 'user_permissions']:
                if field in form.base_fields:
                    del form.base_fields[field]
        
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
from .models import IndividualKYC, OrganizationKYC, KycAudit, Assessment


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("user", "skill_focus", "score", "get_grade", "total_questions", "correct_answers", "created_at")
    list_filter = ("created_at", "score")
    search_fields = ("user__username", "user__email", "skill_focus")
    readonly_fields = ("user", "skill_focus", "total_questions", "correct_answers", "wrong_answers", 
                      "total_time_seconds", "score", "questions_data", "created_at")
    
    def has_add_permission(self, request):
        """Prevent manual creation of assessments"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete assessments"""
        return request.user.is_superuser


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
