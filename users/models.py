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
    
    def get_daily_application_count(self):
        """Get today's application count for unverified users"""
        if self.is_kyc_verified:
            return 0  # No limit for verified users
        from django.utils import timezone
        from organization.models import Application
        today = timezone.now().date()
        return Application.objects.filter(applicant=self, created_at__date=today).count()
    
    def can_apply_today(self):
        """Check if user can apply for jobs today"""
        if self.is_kyc_verified:
            return True
        return self.get_daily_application_count() < 2
    
    def can_post_jobs(self):
        """Check if organization can post jobs"""
        return self.is_organization() and self.is_kyc_verified

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
    
    def get_kyc_status(self):
        """Get user's KYC status and type"""
        try:
            if self.is_applicant():
                kyc = IndividualKYC.objects.get(user=self)
                return {'type': 'individual', 'status': kyc.status, 'current_step': kyc.current_step}
            else:
                kyc = OrganizationKYC.objects.get(user=self)
                return {'type': 'organization', 'status': kyc.status, 'current_step': kyc.current_step}
        except (IndividualKYC.DoesNotExist, OrganizationKYC.DoesNotExist):
            return {'type': 'individual' if self.is_applicant() else 'organization', 'status': None, 'current_step': 1}
    
    def needs_kyc_banner(self):
        """Check if user should see KYC completion banner"""
        if self.is_kyc_verified:
            return False
        try:
            if self.is_applicant():
                kyc = IndividualKYC.objects.get(user=self)
                return kyc.status != 'VERIFIED'
            else:
                kyc = OrganizationKYC.objects.get(user=self)
                return kyc.status != 'VERIFIED'
        except (IndividualKYC.DoesNotExist, OrganizationKYC.DoesNotExist):
            return True


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
    # Track which step the user last saved (1..3)
    current_step = models.IntegerField(default=1)
    # Optional rejection reason set by admin when a KYC is rejected
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class IndividualKYC(KycBase):
    # Step 1 - Personal Basic Info
    full_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    marital_status = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=255, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    email_address = models.EmailField(blank=True)
    permanent_address = models.TextField(blank=True)
    temporary_address = models.TextField(blank=True)
    
    # Step 2 - Identification & Documents
    citizenship_number = models.CharField(max_length=128, blank=True)
    citizenship_issue_date = models.DateField(blank=True, null=True)
    citizenship_issue_district = models.CharField(max_length=100, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    driving_license_number = models.CharField(max_length=50, blank=True)
    
    # Document uploads
    citizenship_front = models.ImageField(upload_to='kyc/individual/citizenship/', blank=True, null=True)
    citizenship_back = models.ImageField(upload_to='kyc/individual/citizenship/', blank=True, null=True)
    passport_photo = models.ImageField(upload_to='kyc/individual/passport/', blank=True, null=True)
    driving_license = models.ImageField(upload_to='kyc/individual/license/', blank=True, null=True)
    recent_photo = models.ImageField(upload_to='kyc/individual/photos/', blank=True, null=True)
    address_proof = models.FileField(upload_to='kyc/individual/address/', blank=True, null=True)
    
    # Step 3 - Additional Verification & Declarations
    father_name = models.CharField(max_length=255, blank=True)
    mother_name = models.CharField(max_length=255, blank=True)
    grandfather_name = models.CharField(max_length=255, blank=True)
    spouse_name = models.CharField(max_length=255, blank=True)
    expected_monthly_transaction = models.CharField(max_length=100, blank=True)
    annual_income_range = models.CharField(max_length=100, blank=True)
    purpose_of_account = models.CharField(max_length=255, blank=True)
    is_pep = models.BooleanField(default=False)
    is_fatca = models.BooleanField(default=False)
    user_signature = models.ImageField(upload_to='kyc/individual/signatures/', blank=True, null=True)
    
    # Legacy fields
    id_document = models.FileField(upload_to='kyc/individual/docs/', blank=True, null=True)
    selfie = models.ImageField(upload_to='kyc/individual/selfies/', blank=True, null=True)
    additional_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"IndividualKYC({self.user.username}, {self.status})"


class OrganizationKYC(KycBase):
    # Step 1 - Organization Basic Info
    org_name = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=128, blank=True)
    registration_date = models.DateField(blank=True, null=True)
    organization_type = models.CharField(max_length=100, blank=True)
    pan_vat_number = models.CharField(max_length=20, blank=True)
    industry_type = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    email_address = models.EmailField(blank=True)
    registered_address = models.TextField(blank=True)
    operating_address = models.TextField(blank=True)
    
    # Step 2 - Documents Upload
    registration_certificate = models.FileField(upload_to='kyc/organization/registration/', blank=True, null=True)
    pan_vat_certificate = models.FileField(upload_to='kyc/organization/pan/', blank=True, null=True)
    moa_aa = models.FileField(upload_to='kyc/organization/moa/', blank=True, null=True)
    partnership_agreement = models.FileField(upload_to='kyc/organization/partnership/', blank=True, null=True)
    board_resolution = models.FileField(upload_to='kyc/organization/resolution/', blank=True, null=True)
    office_address_verification = models.FileField(upload_to='kyc/organization/address/', blank=True, null=True)
    signatory_citizenship = models.ImageField(upload_to='kyc/organization/signatory/', blank=True, null=True)
    signatory_photo = models.ImageField(upload_to='kyc/organization/signatory/', blank=True, null=True)
    
    # Step 3 - Additional Verification & Declarations
    major_shareholders = models.JSONField(blank=True, null=True)
    directors_info = models.JSONField(blank=True, null=True)
    authorized_person_declaration = models.TextField(blank=True)
    source_of_funds = models.CharField(max_length=255, blank=True)
    expected_monthly_transaction_volume = models.CharField(max_length=100, blank=True)
    is_pep = models.BooleanField(default=False)
    is_fatca = models.BooleanField(default=False)
    organization_stamp = models.ImageField(upload_to='kyc/organization/stamps/', blank=True, null=True)
    
    # Legacy fields
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


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('KYC_VERIFIED', 'KYC Verified'),
        ('KYC_REJECTED', 'KYC Rejected'),
        ('KYC_SUBMITTED', 'KYC Submitted'),
        ('KYC_MORE_INFO', 'KYC Request More Info'),
        ('JOB_APPLICATION', 'Job Application'),
        ('JOB_SHORTLIST', 'Job Shortlist'),
        ('JOB_OFFER', 'Job Offer'),
        ('GENERAL', 'General Notification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='GENERAL')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    related_id = models.IntegerField(blank=True, null=True, help_text="ID of related KYC/Job/Application")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

