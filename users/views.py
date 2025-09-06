from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .forms_profile import ApplicantProfileEditForm

from .forms import LoginForm, ApplicantSignUpForm, OrganizationSignUpForm
from organization.models import Job, Application
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model


class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class DashboardView(TemplateView):
    template_name = "dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context



from django.contrib.auth import logout
from django.views import View
from django.http import HttpResponseRedirect

class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, "logout.html")


def signup_select(request):
    return render(request, "users/signup2.html")


def signup_applicant(request):
    if request.method == "POST":
        form = ApplicantSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:dashboard")
    else:
        form = ApplicantSignUpForm()
    return render(request, "users/job_signup.html", {"form": form})


def signup_organization(request):
    if request.method == "POST":
        form = OrganizationSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:dashboard")
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
        return redirect("users:profile")
    if request.method == "POST":
        form = ApplicantProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("users:profile")
    else:
        form = ApplicantProfileEditForm(instance=user)
    return render(request, "users/profile_edit.html", {"form": form})

def dash_jobs(request):
    jobs = Job.objects.all().values('id', 'title', 'location', 'salary')
    return render(request, "users/dash_jobs.html", {"jobs": list(jobs)})
def organizations(request):
    return render(request,"users/organizations.html")
def payment(request):
    return render(request,"users/payment.html")
