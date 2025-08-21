from django.contrib import admin
from .models import Job, Application


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "posted_by", "job_type", "location", "created_at")
    search_fields = ("title", "description", "requirements", "location")
    list_filter = ("job_type", "location", "created_at")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("job__title", "applicant__username")

from django.contrib import admin

# Register your models here.
