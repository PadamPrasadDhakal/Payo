from django.db import models
from django.conf import settings

# Create your models here.

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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="org_jobs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(blank=True, null=True)
    # poster = models.ImageField(upload_to='.posters/', blank=True, null=True)    


    class Meta:
        app_label = 'organization'
        db_table = 'organization_job'
        verbose_name = 'Organization Job'
        verbose_name_plural = 'Organization Jobs'

    def __str__(self) -> str:
        return f"{self.title}"

class Application(models.Model):
    resume = models.FileField(upload_to="applications/resumes/", blank=True, null=True)
    class Status(models.TextChoices):
        APPLIED = "AP", "Applied"
        SHORTLISTED = "SL", "Shortlisted"
        REJECTED = "RJ", "Rejected"
        HIRED = "HD", "Hired"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="org_applications"
    )
    cover_letter = models.TextField(blank=True)
    # resume field removed
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.APPLIED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'organization'
        db_table = 'organization_application'
        unique_together = ("job", "applicant")
        verbose_name = 'Organization Application'
        verbose_name_plural = 'Organization Applications'

    def __str__(self) -> str:
        return f"{self.applicant.username}  {self.job.title} ({self.get_status_display()})"
