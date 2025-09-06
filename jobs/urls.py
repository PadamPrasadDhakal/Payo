from django.urls import path
from .views import JobListView, JobDetailView, JobCreateView, apply_job
from .api import jobs_json


urlpatterns = [
    path("", JobListView.as_view(), name="list"),
    path("post/", JobCreateView.as_view(), name="post"),
    path("<int:pk>/", JobDetailView.as_view(), name="detail"),
    path("<int:pk>/apply/", apply_job, name="apply"),
    path("api/jobs/", jobs_json, name="jobs_json"),
]


