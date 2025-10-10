from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
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

    # Common fields for all users
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    official_name = models.CharField(max_length=255, blank=True,null=True)

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

    # Token system fields
    tokens_left = models.IntegerField(default=7)
    last_token_reset = models.DateTimeField(auto_now_add=True)
    tokens_restored_flag = models.BooleanField(default=False)

    def is_organization(self) -> bool:
        return self.user_type == self.UserType.ORGANIZATION

    def is_applicant(self) -> bool:
        return self.user_type == self.UserType.APPLICANT


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey('organization.Job', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


