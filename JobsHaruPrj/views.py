from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from organization.models import Job, Application

def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_organization():
            # Organizations go to their profile/dashboard
            return redirect('organization:profile')
        else:
            # Applicants go to their dashboard
            return render(request, "dashboard.html")
    return render(request, "home.html")

def logout_view(request):
    logout(request)
    return redirect('home')
# def organizations(request):
#     return redirect('organizations')

def organizations(request):
    # Example: pass an empty list or your actual organizations queryset
    organizations = []
    return render(request, "users/organizations.html", {"organizations": organizations}) 

def internships(request):
    # Example: pass an empty list or your actual organizations queryset
    internships = []
    return render(request, "users/internships.html", {"internships": internships}) 

def assessments(request):
    # Example: pass an empty list or your actual assessments queryset
    assessments = []
    return render(request, "users/assessments.html", {"assessments": assessments}) 
def profile(request):
    # Example: pass an empty list or your actual assessments queryset
    profile = []
    return render(request, "users/profile.html", {"profile": profile})
def payment(request):
    payment = []
    return render(request, "users/payment.html", {"payment": payment})