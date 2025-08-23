from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


TAILWIND_INPUT = "w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": TAILWIND_INPUT, "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": TAILWIND_INPUT, "placeholder": "Password"}))


class ApplicantSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "skills",
            "education",
            "experience",
            "resume",
        )

    def save(self, commit: bool = True):
        user: User = super().save(commit=False)
        user.user_type = User.UserType.APPLICANT
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
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password"})


class OrganizationSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
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
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password"})


