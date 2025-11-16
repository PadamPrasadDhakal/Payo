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
    )
    list_display = ("username", "email", "user_type", "is_staff", "is_active")

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
