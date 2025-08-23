from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home_view(request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html")
    return render(request, "home.html")
