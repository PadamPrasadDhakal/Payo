from django import forms
from .models import IndividualKYC, OrganizationKYC
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import json

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png']
ALLOWED_DOC_TYPES = ['application/pdf', 'image/jpeg', 'image/png']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_phone(value):
    if value and (not value.isdigit() or len(value) != 10):
        raise ValidationError('Phone number must be exactly 10 digits')

def validate_pan(value):
    if value and (not value.isdigit() or len(value) != 9):
        raise ValidationError('PAN must be exactly 9 digits')

def validate_file(f):
    if f:
        if f.size > MAX_FILE_SIZE:
            raise ValidationError('File size must be <= 5MB')
        if not f.name.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            raise ValidationError('Invalid file type. Acceptable types: JPG, PNG, PDF')

def validate_image(f):
    if f:
        if f.size > MAX_FILE_SIZE:
            raise ValidationError('Image size must be <= 5MB')
        if not f.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError('Invalid image type. Acceptable types: JPG, PNG')

# Individual KYC Forms
class IndividualKYCStep1Form(forms.ModelForm):
    class Meta:
        model = IndividualKYC
        fields = [
            'full_name', 'date_of_birth', 'gender', 'nationality', 'marital_status',
            'occupation', 'education_level', 'mobile_number', 'email_address',
            'permanent_address', 'temporary_address'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[
                ('', 'Select Gender'),
                ('Male', 'Male'),
                ('Female', 'Female'),
                ('Other', 'Other')
            ]),
            'marital_status': forms.Select(choices=[
                ('', 'Select Status'),
                ('Single', 'Single'),
                ('Married', 'Married'),
                ('Divorced', 'Divorced'),
                ('Widowed', 'Widowed')
            ]),
            'permanent_address': forms.Textarea(attrs={'rows': 3}),
            'temporary_address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if mobile:
            validate_phone(mobile)
        return mobile

    def clean_email_address(self):
        email = self.cleaned_data.get('email_address')
        if email:
            validate_email(email)
        return email

class IndividualKYCStep2Form(forms.ModelForm):
    class Meta:
        model = IndividualKYC
        fields = [
            'citizenship_number', 'citizenship_issue_date', 'citizenship_issue_district',
            'passport_number', 'driving_license_number', 'citizenship_front',
            'citizenship_back', 'passport_photo', 'driving_license', 'recent_photo',
            'address_proof'
        ]
        widgets = {
            'citizenship_issue_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_citizenship_front(self):
        f = self.cleaned_data.get('citizenship_front')
        if f:
            validate_image(f)
        return f

    def clean_citizenship_back(self):
        f = self.cleaned_data.get('citizenship_back')
        if f:
            validate_image(f)
        return f

    def clean_recent_photo(self):
        f = self.cleaned_data.get('recent_photo')
        if f:
            validate_image(f)
        return f

    def clean_address_proof(self):
        f = self.cleaned_data.get('address_proof')
        if f:
            validate_file(f)
        return f

class IndividualKYCStep3Form(forms.ModelForm):
    declaration = forms.BooleanField(required=True, label="I confirm that all information provided is true and accurate")
    
    class Meta:
        model = IndividualKYC
        fields = [
            'father_name', 'mother_name', 'grandfather_name', 'spouse_name',
            'expected_monthly_transaction', 'annual_income_range', 'purpose_of_account',
            'is_pep', 'is_fatca', 'user_signature'
        ]
        widgets = {
            'expected_monthly_transaction': forms.Select(choices=[
                ('', 'Select Range'),
                ('Below 50,000', 'Below Rs. 50,000'),
                ('50,000-200,000', 'Rs. 50,000 - 2,00,000'),
                ('200,000-500,000', 'Rs. 2,00,000 - 5,00,000'),
                ('Above 500,000', 'Above Rs. 5,00,000')
            ]),
            'annual_income_range': forms.Select(choices=[
                ('', 'Select Range'),
                ('Below 500,000', 'Below Rs. 5,00,000'),
                ('500,000-1,000,000', 'Rs. 5,00,000 - 10,00,000'),
                ('1,000,000-2,000,000', 'Rs. 10,00,000 - 20,00,000'),
                ('Above 2,000,000', 'Above Rs. 20,00,000')
            ]),
        }

    def clean_user_signature(self):
        f = self.cleaned_data.get('user_signature')
        if f:
            validate_image(f)
        return f

# Organization KYC Forms
class OrganizationKYCStep1Form(forms.ModelForm):
    class Meta:
        model = OrganizationKYC
        fields = [
            'org_name', 'registration_number', 'registration_date', 'organization_type',
            'pan_vat_number', 'industry_type', 'contact_number', 'email_address',
            'registered_address', 'operating_address'
        ]
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'organization_type': forms.Select(choices=[
                ('', 'Select Type'),
                ('Company', 'Company'),
                ('Firm', 'Firm'),
                ('NGO', 'NGO'),
                ('School', 'School'),
                ('Hospital', 'Hospital'),
                ('Other', 'Other')
            ]),
            'registered_address': forms.Textarea(attrs={'rows': 3}),
            'operating_address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number')
        if contact:
            validate_phone(contact)
        return contact

    def clean_pan_vat_number(self):
        pan = self.cleaned_data.get('pan_vat_number')
        if pan:
            validate_pan(pan)
        return pan

    def clean_email_address(self):
        email = self.cleaned_data.get('email_address')
        if email:
            validate_email(email)
        return email

class OrganizationKYCStep2Form(forms.ModelForm):
    class Meta:
        model = OrganizationKYC
        fields = [
            'registration_certificate', 'pan_vat_certificate', 'moa_aa',
            'partnership_agreement', 'board_resolution', 'office_address_verification',
            'signatory_citizenship', 'signatory_photo'
        ]

    def clean_registration_certificate(self):
        f = self.cleaned_data.get('registration_certificate')
        if f:
            validate_file(f)
        return f

    def clean_pan_vat_certificate(self):
        f = self.cleaned_data.get('pan_vat_certificate')
        if f:
            validate_file(f)
        return f

    def clean_signatory_citizenship(self):
        f = self.cleaned_data.get('signatory_citizenship')
        if f:
            validate_image(f)
        return f

    def clean_signatory_photo(self):
        f = self.cleaned_data.get('signatory_photo')
        if f:
            validate_image(f)
        return f

class OrganizationKYCStep3Form(forms.ModelForm):
    declaration = forms.BooleanField(required=True, label="I confirm that all information provided is true and accurate")
    shareholders_json = forms.CharField(widget=forms.HiddenInput(), required=False)
    directors_json = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = OrganizationKYC
        fields = [
            'authorized_person_declaration', 'source_of_funds',
            'expected_monthly_transaction_volume', 'is_pep', 'is_fatca',
            'organization_stamp'
        ]
        widgets = {
            'expected_monthly_transaction_volume': forms.Select(choices=[
                ('', 'Select Range'),
                ('Below 1,000,000', 'Below Rs. 10,00,000'),
                ('1,000,000-5,000,000', 'Rs. 10,00,000 - 50,00,000'),
                ('5,000,000-10,000,000', 'Rs. 50,00,000 - 1,00,00,000'),
                ('Above 10,000,000', 'Above Rs. 1,00,00,000')
            ]),
            'authorized_person_declaration': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_organization_stamp(self):
        f = self.cleaned_data.get('organization_stamp')
        if f:
            validate_image(f)
        return f

    def clean(self):
        cleaned_data = super().clean()
        
        # Parse JSON fields
        shareholders_json = cleaned_data.get('shareholders_json')
        directors_json = cleaned_data.get('directors_json')
        
        if shareholders_json:
            try:
                shareholders = json.loads(shareholders_json)
                cleaned_data['major_shareholders'] = shareholders
            except json.JSONDecodeError:
                raise ValidationError("Invalid shareholders data")
        
        if directors_json:
            try:
                directors = json.loads(directors_json)
                cleaned_data['directors_info'] = directors
            except json.JSONDecodeError:
                raise ValidationError("Invalid directors data")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set JSON fields from cleaned data
        if 'major_shareholders' in self.cleaned_data:
            instance.major_shareholders = self.cleaned_data['major_shareholders']
        if 'directors_info' in self.cleaned_data:
            instance.directors_info = self.cleaned_data['directors_info']
        
        if commit:
            instance.save()
        return instance