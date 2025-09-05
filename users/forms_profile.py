from django import forms
from .models import User

TAILWIND_INPUT = "w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"

class ApplicantProfileEditForm(forms.ModelForm):
    EDUCATION_QUALIFICATIONS = [
        ("", "Select qualification"),
        ("SEE/SLC", "SEE/SLC"),
        ("+2/Intermediate", "+2/Intermediate"),
        ("Bachelor", "Bachelor"),
        ("Master", "Master"),
        ("PhD", "PhD"),
        ("Other", "Other"),
    ]
    profile_photo = forms.ImageField(required=False)
    education_qualification = forms.ChoiceField(choices=EDUCATION_QUALIFICATIONS, required=False)
    education_institute = forms.CharField(required=False)
    education_address = forms.CharField(required=False)
    education_cgpa = forms.DecimalField(max_digits=4, decimal_places=2, required=False)
    education_cgpa_scale = forms.ChoiceField(choices=[("4", "4"), ("10", "10")], required=False)
    speciality = forms.CharField(required=False)
    hobby = forms.CharField(required=False)
    internship = forms.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "profile_photo",
            "skills",
            "education_qualification",
            "education_institute",
            "education_address",
            "education_cgpa",
            "education_cgpa_scale",
            "speciality",
            "hobby",
            "internship",
            "experience",
            "resume",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css = TAILWIND_INPUT
            if getattr(field.widget, 'input_type', '') == 'file':
                css = "block w-full text-sm text-gray-700 border border-gray-300 rounded-md cursor-pointer bg-white px-3 py-2"
            field.widget.attrs.update({"class": css})
        self.fields["education_institute"].widget.attrs.update({"placeholder": "Institute name"})
        self.fields["education_address"].widget.attrs.update({"placeholder": "Institute address"})
        self.fields["education_cgpa"].widget.attrs.update({"placeholder": "CGPA"})
        self.fields["speciality"].widget.attrs.update({"placeholder": "Speciality (optional)"})
        self.fields["hobby"].widget.attrs.update({"placeholder": "Hobby (optional)"})
        self.fields["internship"].widget.attrs.update({"placeholder": "Internship experience (optional)"})
