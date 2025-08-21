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
                    "education",
                    "experience",
                )
            },
        ),
    )
    list_display = ("username", "email", "user_type", "is_staff", "is_active")

from django.contrib import admin

# Register your models here.
