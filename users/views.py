from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms_profile import ApplicantProfileEditForm

from .forms import LoginForm, ApplicantSignUpForm, OrganizationSignUpForm


class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm



from django.contrib.auth import logout
from django.views import View
from django.http import HttpResponseRedirect

class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, "logout.html")


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


@login_required
def profile_edit(request):
    user = request.user
    if user.user_type != user.UserType.APPLICANT:
        return redirect("profile")
    if request.method == "POST":
        form = ApplicantProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ApplicantProfileEditForm(instance=user)
    return render(request, "users/profile_edit.html", {"form": form})

from django.shortcuts import render

# Create your views here.
