from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from organization.models import Job, Application

def home_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'user_type') and request.user.user_type == 'ORG':
            # Show Applications per Job table on home page
            jobs = Job.objects.filter(posted_by=request.user)
            job_count = jobs.count()
            applications_by_job = {job: job.applications.count() for job in jobs}
            return render(request, "org_home.html", {
                "job_count": job_count,
                "applications_by_job": applications_by_job,
            })
        else:
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