from django.urls import path
from django.shortcuts import redirect
from django.views.generic import TemplateView
from .views import (
    organization_list_view,
    JobListView,
    JobDetailView,
    JobCreateView,
    apply_job,
    applications_overview,
    application_detail,
    classify,
    match_resumes,
    org_dashboard,
    org_jobs,
    OrgJobCreateView,
    update_application_status,
)

app_name = "organization"

urlpatterns = [
    path("pricing/", TemplateView.as_view(template_name="organization_pricing.html"), name="pricing"),
    path("dashboard/", org_dashboard, name="dashboard"),
    path("jobs/", JobListView.as_view(), name="job-list"),
    path("jobs/new/", OrgJobCreateView.as_view(), name="post-job"),
    path("", organization_list_view, name="list"),
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job-detail"),
    path("jobs/<int:pk>/apply/", apply_job, name="apply-job"),
    path("applications/", applications_overview, name="applications-overview"),
    path("applications/<int:pk>/", application_detail, name="application-detail"),
    path("applications/update-status/", update_application_status, name="update-application-status"),
    path("classify/", classify, name="classify"),
    path("match_resumes/", match_resumes, name="match-resumes"),
    path("users/logout/", lambda request: redirect('/users/logout/')),  # Redirect to users logout
]
