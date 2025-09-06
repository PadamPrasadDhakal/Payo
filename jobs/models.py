from django.db import models
from django.conf import settings


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ("FT", "Full Time"),
        ("PT", "Part Time"),
        ("CT", "Contract"),
        ("IN", "Internship"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    salary = models.CharField(max_length=255, blank=True)
    job_type = models.CharField(max_length=2, choices=JOB_TYPE_CHOICES, default="FT")
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title}"


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "AP", "Applied"
        SHORTLISTED = "SL", "Shortlisted"
        REJECTED = "RJ", "Rejected"
        HIRED = "HD", "Hired"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to="applications/resumes/", blank=True, null=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.APPLIED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "applicant")

    def __str__(self) -> str:
        return f"{self.applicant.username} → {self.job.title} ({self.get_status_display()})"

# Create your models here.
