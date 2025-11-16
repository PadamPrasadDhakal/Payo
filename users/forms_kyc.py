from django import forms
from .models import IndividualKYC, OrganizationKYC
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_phone(value):
    if value and (not value.isdigit() or len(value) != 10):
        raise ValidationError('Phone number must be exactly 10 digits')


def validate_pan(value):
    if value and (not value.isdigit() or len(value) != 9):
        raise ValidationError('PAN must be exactly 9 digits')


def validate_file(f):
    if f:
        if getattr(f, 'content_type', '') not in ALLOWED_IMAGE_TYPES and not f.name.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            raise ValidationError('Invalid file type. Acceptable types: JPG, PNG, PDF')
        if f.size > MAX_FILE_SIZE:
            raise ValidationError('File size must be <= 5MB')


class IndividualKYCStep1Form(forms.ModelForm):
    class Meta:
        model = IndividualKYC
        fields = ['full_name', 'date_of_birth', 'nationality']

    contact_mobile = forms.CharField(required=False, validators=[validate_phone])
    email = forms.EmailField(required=False)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            validate_email(email)
        return email


class IndividualKYCStep2Form(forms.ModelForm):
    class Meta:
        model = IndividualKYC
        fields = ['citizenship_number', 'id_document', 'selfie']

    def clean_id_document(self):
        f = self.cleaned_data.get('id_document')
        validate_file(f)
        return f

    def clean_selfie(self):
        f = self.cleaned_data.get('selfie')
        validate_file(f)
        return f


class IndividualKYCStep3Form(forms.ModelForm):
    class Meta:
        model = IndividualKYC
        fields = ['additional_info']

    declaration = forms.BooleanField(required=True)


class OrganizationKYCStep1Form(forms.ModelForm):
    class Meta:
        model = OrganizationKYC
        fields = ['org_name', 'registration_number', 'registration_date', 'org_name']

    contact_number = forms.CharField(required=False, validators=[validate_phone])
    email = forms.EmailField(required=False)

    def clean_registration_number(self):
        val = self.cleaned_data.get('registration_number')
        if val and not val.isalnum():
            raise ValidationError('Registration number must be alphanumeric')
        return val


class OrganizationKYCStep2Form(forms.ModelForm):
    class Meta:
        model = OrganizationKYC
        fields = ['incorporation_certificate', 'directors', 'shareholders']

    def clean_incorporation_certificate(self):
        f = self.cleaned_data.get('incorporation_certificate')
        validate_file(f)
        return f


class OrganizationKYCStep3Form(forms.ModelForm):
    class Meta:
        model = OrganizationKYC
        fields = ['additional_info']

    declaration = forms.BooleanField(required=True)
