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
    phone = models.CharField(max_length=10, blank=True, null=True)
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

    # Profile boosting fields - count achievements regardless of final status
    shortlisted_count = models.IntegerField(default=0, help_text="Total times shortlisted (regardless of final outcome)")
    selected_count = models.IntegerField(default=0, help_text="Total times selected for interview (regardless of final outcome)")
    hired_count = models.IntegerField(default=0, help_text="Total times hired")
    profile_score = models.IntegerField(default=0, help_text="Calculated profile strength score")
    
    # KYC flag
    is_kyc_verified = models.BooleanField(default=False)
    kyc_last_submitted = models.DateTimeField(blank=True, null=True)

    def is_organization(self) -> bool:
        return self.user_type == self.UserType.ORGANIZATION

    def is_applicant(self) -> bool:
        return self.user_type == self.UserType.APPLICANT

    def update_profile_score(self):
        """Calculate and update profile strength score based on achievements"""
        if self.is_applicant():
            # Base score calculation
            score = 0
            
            # Points for completeness
            if self.profile_photo:
                score += 10
            if self.resume:
                score += 20
            if self.skills:
                score += 15
            if self.education_qualification:
                score += 10
            if self.experience:
                score += 15
            
            # Achievement bonuses (these boost the profile regardless of final outcome)
            score += self.shortlisted_count * 25  # 25 points per shortlist
            score += self.selected_count * 50     # 50 points per selection
            score += self.hired_count * 100       # 100 points per hire
            
            # Cap at reasonable maximum
            self.profile_score = min(score, 1000)
            self.save(update_fields=['profile_score'])
        
        return self.profile_score

    def increment_achievement(self, achievement_type):
        """Increment achievement counters and update profile score"""
        if not self.is_applicant():
            return
            
        if achievement_type == 'shortlisted':
            self.shortlisted_count += 1
        elif achievement_type == 'selected':
            self.selected_count += 1
        elif achievement_type == 'hired':
            self.hired_count += 1
        
        self.save()
        self.update_profile_score()
        print(f"Profile updated for {self.username}: shortlisted={self.shortlisted_count}, selected={self.selected_count}, hired={self.hired_count}, score={self.profile_score}")


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey('organization.Job', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


class KycBase(models.Model):
    class KycStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_records')
    status = models.CharField(max_length=16, choices=KycStatus.choices, default=KycStatus.DRAFT)
    submitted_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class IndividualKYC(KycBase):
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True)
    citizenship_number = models.CharField(max_length=128, blank=True)
    id_document = models.FileField(upload_to='kyc/individual/docs/', blank=True, null=True)
    selfie = models.ImageField(upload_to='kyc/individual/selfies/', blank=True, null=True)
    additional_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"IndividualKYC({self.user.username}, {self.status})"


class OrganizationKYC(KycBase):
    org_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=128, blank=True)
    registered_address = models.CharField(max_length=512, blank=True)
    incorporation_certificate = models.FileField(upload_to='kyc/organization/docs/', blank=True, null=True)
    directors = models.JSONField(blank=True, null=True)
    shareholders = models.JSONField(blank=True, null=True)
    additional_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"OrganizationKYC({self.org_name}, {self.status})"


class KycAudit(models.Model):
    KYC_TYPE_CHOICES = (
        ('IND', 'Individual'),
        ('ORG', 'Organization'),
    )
    kyc_type = models.CharField(max_length=3, choices=KYC_TYPE_CHOICES)
    kyc_id = models.IntegerField()
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kyc_audits')
    action = models.CharField(max_length=64)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KycAudit({self.kyc_type}#{self.kyc_id} by {self.actor})"


