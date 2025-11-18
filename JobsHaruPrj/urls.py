from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from .views import *
# from .views import organizations
from django.views.generic import TemplateView
from api.debug import debug_tokens


def plans_redirect(request):
    """Redirect /plans/ to organization pricing if logged in as organization, otherwise to home"""
    if request.user.is_authenticated and request.user.is_organization():
        return redirect('organization:pricing')
    else:
        return redirect('home')


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
    path("contact/", TemplateView.as_view(template_name="contact.html"), name="contact"),
    path("individual/", TemplateView.as_view(template_name="individual.html"), name="individual"),
    path("organization/", include(("organization.urls", "organization"), namespace="organization")),
    path("api/", include("api.urls")),
    path("debug-tokens/", debug_tokens, name="debug_tokens"),
    path("users/", include(("users.urls", "users"), namespace="users")),
    # path("jobs/", include(("jobs.urls", "jobs"), namespace="jobs")),  # Disabled - using organization app
    path('accounts/', include('allauth.urls')),
    path('logout/',logout_view,name='logout'),
    path('organizations/', organizations, name='organizations'),
    path('internships/',internships, name='internships'),
    path('assessments/',assessments, name='assessments'),
    path('profile/',profile, name='profile'),
    path('plans/', plans_redirect, name='plans'),
    path('payment/',payment, name='payment'),
    path('makecv/',include(("makecv.urls", "makecv"), namespace="makecv")),
    # path('makecv/',include(("makecv.urls", "makecv"), namespace="makecv")),
    # path('logouts/',logouts,name='logouts'),
    
# path('Organizations/', organizations),  # optional, not recommended
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
URL configuration for jobsharuPrj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
 
