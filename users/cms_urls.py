from django.urls import path
from .views import cms_dashboard, cms_kyc_detail, cms_login, cms_logout

app_name = 'cms'

urlpatterns = [
    path("", cms_dashboard, name="dashboard"),
    path("kyc/<str:kyc_type>/<int:kyc_id>/", cms_kyc_detail, name="kyc_detail"),
    path("login/", cms_login, name="login"),
    path("logout/", cms_logout, name="logout"),
]
