from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

# Create your models here.

class Payment(models.Model):
    PLAN_CHOICES = [
        ('starter', 'Starter - NPR 1,000/month'),
        ('growth', 'Growth - NPR 3,000/month'),
        ('enterprise', 'Enterprise - NPR 7,000/month'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
        ('credit_card', 'Credit Card'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PREMIUM_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    organization = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    premium_status = models.CharField(max_length=20, choices=PREMIUM_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Payment details
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    premium_approved_at = models.DateTimeField(blank=True, null=True)
    
    # Subscription details
    subscription_start = models.DateTimeField(blank=True, null=True)
    subscription_end = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        app_label = 'organization'
        db_table = 'organization_payment'
        verbose_name = 'Organization Payment'
        verbose_name_plural = 'Organization Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.organization.username} - {self.plan} - {self.get_status_display()}"
    
    def get_plan_price(self):
        """Return price for the plan"""
        prices = {
            'starter': 1000,
            'growth': 3000,
            'enterprise': 7000,
        }
        return prices.get(self.plan, 0)
    
    def get_plan_display_name(self):
        """Return readable plan name"""
        names = {
            'starter': 'Starter Plan',
            'growth': 'Growth Plan',
            'enterprise': 'Enterprise Plan',
        }
        return names.get(self.plan, 'Unknown Plan')
    
    def is_active_subscription(self):
        """Check if subscription is active"""
        if self.status != 'completed':
            return False
        if not self.subscription_end:
            return False
        return self.subscription_end > timezone.now()

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
    
    def get_closing_date(self):
        """Get job closing date - either deadline or 30 days from posting"""
        if self.deadline:
            return self.deadline
        # Default to 30 days from posting if no deadline set
        from datetime import timedelta
        return self.created_at + timedelta(days=30)
    
    def is_expired(self):
        """Check if job posting has expired"""
        from django.utils import timezone
        return self.get_closing_date() < timezone.now()
    
    def days_remaining(self):
        """Get number of days remaining for application"""
        from django.utils import timezone
        if self.is_expired():
            return 0
        delta = self.get_closing_date() - timezone.now()
        return max(0, delta.days)

class Application(models.Model):
    resume = models.FileField(upload_to="applications/resumes/", blank=True, null=True)
    class Status(models.TextChoices):
        PENDING = "PD", "Pending"
        REVIEWING = "RV", "Reviewing"
        SHORTLISTED = "SL", "Shortlisted"
        SELECTED = "SE", "Selected"
        REJECTED = "RJ", "Rejected"
        WITHDRAWN = "WD", "Withdrawn"
        HIRED = "HD", "Hired"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="org_applications"
    )
    cover_letter = models.TextField(blank=True)
    # resume field removed
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, help_text="Internal notes from reviewers")

    class Meta:
        app_label = 'organization'
        db_table = 'organization_application'
        unique_together = ("job", "applicant")
        verbose_name = 'Organization Application'
        verbose_name_plural = 'Organization Applications'

    def __str__(self) -> str:
        return f"{self.applicant.username}  {self.job.title} ({self.get_status_display()})"
    
    def get_status_color(self):
        """Return CSS color class for status"""
        colors = {
            'PD': 'text-yellow-600 bg-yellow-100',
            'RV': 'text-blue-600 bg-blue-100',
            'SL': 'text-purple-600 bg-purple-100',
            'SE': 'text-green-600 bg-green-100',
            'RJ': 'text-red-600 bg-red-100',
            'WD': 'text-gray-600 bg-gray-100',
            'HD': 'text-emerald-600 bg-emerald-100',
        }
        return colors.get(self.status, 'text-gray-600 bg-gray-100')
    
    def is_active(self):
        """Check if application is still active (not rejected/withdrawn/hired)"""
        return self.status not in ['RJ', 'WD', 'HD']
