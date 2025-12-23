from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .models import User


TAILWIND_INPUT = "w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": TAILWIND_INPUT, "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": TAILWIND_INPUT, "placeholder": "Password"}))


class ApplicantSignUpForm(UserCreationForm):
    EDUCATION_QUALIFICATIONS = [
        ("", "Select qualification"),
        ("SEE/SLC", "SEE/SLC"),
        ("+2/Intermediate", "+2/Intermediate"),
        ("Bachelor", "Bachelor"),
        ("Master", "Master"),
        ("PhD", "PhD"),
        ("Other", "Other"),
    ]

    official_name = forms.CharField(max_length=255, required=True, label="Full Name")
    phone = forms.CharField(max_length=20, required=True, label="Phone Number")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label="Address")
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
        fields = (
            "username",
            "email",
            "official_name",
            "phone",
            "address",
            "password1",
            "password2",
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
        )

    def save(self, commit: bool = True):
        user: User = super().save(commit=False)
        user.user_type = User.UserType.APPLICANT
        user.profile_photo = self.cleaned_data.get("profile_photo")
        user.education_qualification = self.cleaned_data.get("education_qualification")
        user.education_institute = self.cleaned_data.get("education_institute")
        user.education_address = self.cleaned_data.get("education_address")
        user.education_cgpa = self.cleaned_data.get("education_cgpa")
        user.education_cgpa_scale = self.cleaned_data.get("education_cgpa_scale")
        user.speciality = self.cleaned_data.get("speciality")
        user.hobby = self.cleaned_data.get("hobby")
        user.internship = self.cleaned_data.get("internship")
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css = TAILWIND_INPUT
            if getattr(field.widget, 'input_type', '') == 'file':
                css = "block w-full text-sm text-gray-700 border border-gray-300 rounded-md cursor-pointer bg-white px-3 py-2"
            field.widget.attrs.update({"class": css})
        self.fields["username"].widget.attrs.update({"placeholder": "Username"})
        self.fields["email"].widget.attrs.update({"placeholder": "Email"})
        self.fields["phone"].widget.attrs.update({"placeholder": "Phone Number"})
        self.fields["address"].widget.attrs.update({"placeholder": "Address"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password"})
        self.fields["education_institute"].widget.attrs.update({"placeholder": "Institute name"})
        self.fields["education_address"].widget.attrs.update({"placeholder": "Institute address"})
        self.fields["education_cgpa"].widget.attrs.update({"placeholder": "CGPA"})
        self.fields["speciality"].widget.attrs.update({"placeholder": "Speciality (optional)"})
        self.fields["hobby"].widget.attrs.update({"placeholder": "Hobby (optional)"})
        self.fields["internship"].widget.attrs.update({"placeholder": "Internship experience (optional)"})


class OrganizationSignUpForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone",
            "address",
            "password1",
            "password2",
            "organization_name",
            "organization_website",
        )

    def save(self, commit: bool = True):
        user: User = super().save(commit=False)
        user.user_type = User.UserType.ORGANIZATION
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": TAILWIND_INPUT})
        self.fields["username"].widget.attrs.update({"placeholder": "Organization username"})
        self.fields["email"].widget.attrs.update({"placeholder": "Email"})
        self.fields["phone"].widget.attrs.update({"placeholder": "Contact Phone"})
        self.fields["address"].widget.attrs.update({"placeholder": "Organization Address"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password"})


class GoogleUserCompleteProfileForm(forms.ModelForm):
    """Form for Google OAuth users to complete their profile"""
    EDUCATION_QUALIFICATIONS = [
        ("", "Select qualification"),
        ("SEE/SLC", "SEE/SLC"),
        ("+2/Intermediate", "+2/Intermediate"),
        ("Bachelor", "Bachelor"),
        ("Master", "Master"),
        ("PhD", "PhD"),
        ("Other", "Other"),
    ]

    official_name = forms.CharField(max_length=255, required=True, label="Full Name")
    phone = forms.CharField(max_length=20, required=True, label="Phone Number")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label="Address")
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
        fields = (
            "phone",
            "address",
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
        )

    def save(self, commit: bool = True):
        user: User = super().save(commit=False)
        user.user_type = User.UserType.APPLICANT
        user.profile_photo = self.cleaned_data.get("profile_photo")
        user.education_qualification = self.cleaned_data.get("education_qualification")
        user.education_institute = self.cleaned_data.get("education_institute")
        user.education_address = self.cleaned_data.get("education_address")
        user.education_cgpa = self.cleaned_data.get("education_cgpa")
        user.education_cgpa_scale = self.cleaned_data.get("education_cgpa_scale")
        user.speciality = self.cleaned_data.get("speciality")
        user.hobby = self.cleaned_data.get("hobby")
        user.internship = self.cleaned_data.get("internship")
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css = TAILWIND_INPUT
            if getattr(field.widget, 'input_type', '') == 'file':
                css = "block w-full text-sm text-gray-700 border border-gray-300 rounded-md cursor-pointer bg-white px-3 py-2"
            field.widget.attrs.update({"class": css})
        self.fields["phone"].widget.attrs.update({"placeholder": "Phone Number"})
        self.fields["address"].widget.attrs.update({"placeholder": "Address"})
        self.fields["education_institute"].widget.attrs.update({"placeholder": "Institute name"})
        self.fields["education_address"].widget.attrs.update({"placeholder": "Institute address"})
        self.fields["education_cgpa"].widget.attrs.update({"placeholder": "CGPA"})
        self.fields["speciality"].widget.attrs.update({"placeholder": "Speciality (optional)"})
        self.fields["hobby"].widget.attrs.update({"placeholder": "Hobby (optional)"})
        self.fields["internship"].widget.attrs.update({"placeholder": "Internship experience (optional)"})


class ChangePasswordForm(forms.Form):
    """Form for changing user password with old password verification"""
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            "class": TAILWIND_INPUT,
            "placeholder": "Enter your current password",
            "autocomplete": "current-password"
        }),
        required=True
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": TAILWIND_INPUT,
            "placeholder": "Enter your new password",
            "autocomplete": "new-password"
        }),
        required=True
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            "class": TAILWIND_INPUT,
            "placeholder": "Confirm your new password",
            "autocomplete": "new-password"
        }),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        """Verify that the old password is correct"""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                "Your old password was entered incorrectly.",
                code='password_incorrect',
            )
        return old_password

    def clean(self):
        """Verify that new passwords match"""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(
                    "The new passwords do not match.",
                    code='password_mismatch',
                )

        return cleaned_data

    def save(self):
        """Save the new password to the database"""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user
