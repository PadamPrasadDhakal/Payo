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
    applications_dashboard,
    organizations,
    payment,
    apply_job,
    google_signup_redirect,
    add_info
)
from .views import kyc_form_view, cms_dashboard, cms_kyc_detail


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
    path("applications/", applications_dashboard, name="applications_dashboard"),
    path("organizations/",organizations,name="organizations"),
    path("payment/",payment,name="payment"),
    path("apply_job/", apply_job, name="apply_job"),
    path("google-signup-redirect/", google_signup_redirect, name="google_signup_redirect"),
    path("add-info/", add_info, name="add_info"),
    path("kyc/", kyc_form_view, name="kyc_form"),
    path("cms/", cms_dashboard, name="cms_dashboard"),
    path("cms/kyc/<str:kyc_type>/<int:kyc_id>/", cms_kyc_detail, name="cms_kyc_detail"),
    ]


