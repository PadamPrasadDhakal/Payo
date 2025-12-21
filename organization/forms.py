from django import forms
from .models import Job
from users.models import User
from PIL import Image

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "requirements", "location", "salary", "job_type", "deadline"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            # "poster": forms.FileInput(attrs={"accept": "image/png,image/jpeg,image/jpg"}),
        }

    def clean_poster(self):
        poster = self.cleaned_data.get("poster")
        if poster:
            if poster.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Poster image must be less than 10MB.")
            valid_types = ["image/png", "image/jpeg", "image/jpg"]
            # Some browsers only send 'image/jpeg' for both jpeg and jpg
            if poster.content_type not in valid_types and not poster.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise forms.ValidationError("Poster must be a PNG, JPEG, or JPG file.")
            try:
                img = Image.open(poster)
                width, height = img.size
                ratio = width / height
                if not (abs(ratio - 0.75) < 0.05):
                    raise forms.ValidationError("Poster must have a 3:4 aspect ratio.")
            except Exception:
                raise forms.ValidationError("Invalid image file.")
        return poster


TAILWIND_INPUT = "w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"

INDUSTRY_CHOICES = [
    ('', 'Select Industry'),
    ('technology', 'Technology & IT'),
    ('finance', 'Finance & Banking'),
    ('healthcare', 'Healthcare & Medical'),
    ('education', 'Education & Training'),
    ('manufacturing', 'Manufacturing'),
    ('retail', 'Retail & E-commerce'),
    ('hospitality', 'Hospitality & Tourism'),
    ('construction', 'Construction & Real Estate'),
    ('marketing', 'Marketing & Advertising'),
    ('consulting', 'Consulting & Professional Services'),
    ('media', 'Media & Entertainment'),
    ('nonprofit', 'Non-profit & NGO'),
    ('government', 'Government & Public Sector'),
    ('agriculture', 'Agriculture & Food'),
    ('energy', 'Energy & Utilities'),
    ('transportation', 'Transportation & Logistics'),
    ('telecommunications', 'Telecommunications'),
    ('legal', 'Legal Services'),
    ('other', 'Other'),
]


class OrganizationProfileEditForm(forms.ModelForm):
    """Form for editing organization profile details"""
    
    class Meta:
        model = User
        fields = ["organization_name", "organization_website", "organization_industry", "organization_photo", "phone", "address"]
        widgets = {
            "organization_name": forms.TextInput(attrs={
                "class": TAILWIND_INPUT,
                "placeholder": "Organization Name",
                "required": True
            }),
            "organization_website": forms.URLInput(attrs={
                "class": TAILWIND_INPUT,
                "placeholder": "https://example.com",
                "required": False
            }),
            "organization_industry": forms.Select(choices=INDUSTRY_CHOICES, attrs={
                "class": TAILWIND_INPUT,
                "required": True
            }),
            "phone": forms.TextInput(attrs={
                "class": TAILWIND_INPUT,
                "placeholder": "Phone Number",
                "type": "tel"
            }),
            "address": forms.Textarea(attrs={
                "class": TAILWIND_INPUT + " resize-none",
                "placeholder": "Organization Address",
                "rows": 3
            }),
            "organization_photo": forms.FileInput(attrs={
                "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100",
                "accept": "image/*"
            }),
        }
        labels = {
            "organization_name": "Organization Name",
            "organization_website": "Website URL",
            "organization_industry": "Industry/Field",
            "organization_photo": "Logo/Organization Photo",
            "phone": "Phone Number",
            "address": "Address",
        }

    def clean_organization_photo(self):
        photo = self.cleaned_data.get("organization_photo")
        if photo:
            # Check file size (max 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Logo must be less than 5MB.")
            # Check file type
            valid_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"]
            if photo.content_type not in valid_types:
                raise forms.ValidationError("Logo must be a valid image file (PNG, JPEG, JPG, GIF, or WebP).")
        return photo

    def clean_organization_website(self):
        website = self.cleaned_data.get("organization_website")
        if website and not (website.startswith("http://") or website.startswith("https://")):
            raise forms.ValidationError("Website URL must start with http:// or https://")
        return website
