from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


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


