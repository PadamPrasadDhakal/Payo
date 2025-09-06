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
<<<<<<< HEAD
    apply_job,
=======
    payment
>>>>>>> acc2de0434845b98d8ea1a30df331a983bdce10d
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
<<<<<<< HEAD
    path("organizations/", organizations, name="organizations"),
    path("apply_job/", apply_job, name="apply_job"),
]
=======
    path("organizations/",organizations,name="organizations"),
    path("payment/",payment,name="payment"),
    ]
>>>>>>> acc2de0434845b98d8ea1a30df331a983bdce10d


