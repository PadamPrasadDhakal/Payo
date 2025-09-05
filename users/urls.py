from django.urls import path
from .views import (
    UserLoginView,
    UserLogoutView,
    DashboardView,
    signup_select,
    signup_applicant,
    signup_organization,
    profile,
    profile_edit,
    dash_jobs,
    organizations,
)


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("signup/", signup_select, name="signup"),
    path("signup/applicant/", signup_applicant, name="signup_applicant"),
    path("signup/organization/", signup_organization, name="signup_organization"),
    path("profile/", profile, name="profile"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("dash_jobs/", dash_jobs, name="dash_jobs"),
    path("organizations/",organizations,name="organizations")
    ]


