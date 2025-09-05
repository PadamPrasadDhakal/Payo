from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.


class User(AbstractUser):
    class UserType(models.TextChoices):
        ORGANIZATION = "ORG", "Organization"
        APPLICANT = "APP", "Job Applier"

    user_type = models.CharField(
        max_length=3,
        choices=UserType.choices,
        default=UserType.APPLICANT,
    )


    # Organization-specific fields
    organization_name = models.CharField(max_length=255, blank=True)
    organization_website = models.URLField(blank=True)
    organization_photo = models.ImageField(upload_to="organization_photos/", blank=True, null=True)

    # Applicant-specific fields
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    skills = models.TextField(blank=True)
    education_qualification = models.CharField(max_length=100, blank=True)
    education_institute = models.CharField(max_length=255, blank=True)
    education_address = models.CharField(max_length=255, blank=True)
    education_cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    education_cgpa_scale = models.CharField(max_length=10, blank=True)
    speciality = models.CharField(max_length=255, blank=True)
    hobby = models.CharField(max_length=255, blank=True)
    experience = models.TextField(blank=True)
    internship = models.TextField(blank=True)

    def is_organization(self) -> bool:
        return self.user_type == self.UserType.ORGANIZATION

    def is_applicant(self) -> bool:
        return self.user_type == self.UserType.APPLICANT


