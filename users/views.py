from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, ApplicantSignUpForm, OrganizationSignUpForm


class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm


class UserLogoutView(LogoutView):
    next_page = "home"


def signup_select(request):
    return render(request, "users/signup.html")


def signup_applicant(request):
    if request.method == "POST":
        form = ApplicantSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = ApplicantSignUpForm()
    return render(request, "users/job_signup.html", {"form": form})


def signup_organization(request):
    if request.method == "POST":
        form = OrganizationSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = OrganizationSignUpForm()
    return render(request, "users/org_signup.html", {"form": form})


@login_required
def profile(request):
    return render(request, "users/profile.html")

from django.shortcuts import render

# Create your views here.
