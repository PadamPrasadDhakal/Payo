from django import forms
from .models import Job
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
