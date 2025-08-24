from django.urls import path
from .views import (
    UserLoginView,
    UserLogoutView,
    signup_select,
    signup_applicant,
    signup_organization,
    profile,
    profile_edit,
)


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("signup/", signup_select, name="signup"),
    path("signup/applicant/", signup_applicant, name="signup_applicant"),
    path("signup/organization/", signup_organization, name="signup_organization"),
    path("profile/", profile, name="profile"),
    path("profile/edit/", profile_edit, name="profile_edit"),
]


