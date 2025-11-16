from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .forms_profile import ApplicantProfileEditForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .forms import LoginForm, ApplicantSignUpForm, OrganizationSignUpForm, GoogleUserCompleteProfileForm
from organization.models import Job, Application
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import User

from django.contrib.auth import logout
from django.views import View
from django.http import HttpResponseRedirect
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import Http404
from django.core.paginator import Paginator
from users.models import IndividualKYC, OrganizationKYC, KycAudit

class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class DashboardView(TemplateView):
    template_name = "dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context




class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, "logout.html")


def signup_select(request):
    return render(request, "users/signup.html")


def signup_applicant(request):
    if request.method == "POST":
        form = ApplicantSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("users:dashboard")
    else:
        form = ApplicantSignUpForm()
    return render(request, "users/job_signup.html", {"form": form})


def signup_organization(request):
    if request.method == "POST":
        form = OrganizationSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("users:dashboard")
    else:
        form = OrganizationSignUpForm()
    return render(request, "users/org_signup.html", {"form": form})


@login_required
def profile(request):
    return render(request, "users/profile.html")


@login_required
def google_signup_redirect(request):
    """Redirect view for Google OAuth users to complete their profile"""
    user = request.user
    
    # Check if user is coming from Google OAuth and needs to complete profile
    if user.user_type == User.UserType.APPLICANT and not user.official_name:
        return redirect('users:add_info')
    elif user.user_type == User.UserType.APPLICANT:
        return redirect('users:dashboard')
    else:
        # If user is not an applicant, redirect to dashboard
        return redirect('users:dashboard')


@login_required
def add_info(request):
    """View for Google OAuth users to complete their profile"""
    user = request.user
    
    # Only allow applicant users who haven't completed their profile
    if user.user_type != User.UserType.APPLICANT:
        return redirect('users:dashboard')
    
    if request.method == "POST":
        form = GoogleUserCompleteProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Profile completed successfully! You can now apply for jobs.')
            return redirect("users:dashboard")
    else:
        form = GoogleUserCompleteProfileForm(instance=user)
    
    return render(request, "users/add_info.html", {"form": form})


@login_required
def profile_edit(request):
    user = request.user
    if user.user_type != user.UserType.APPLICANT:
        return redirect("users:profile")
    if request.method == "POST":
        form = ApplicantProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("users:profile")
    else:
        form = ApplicantProfileEditForm(instance=user)
    return render(request, "users/profile_edit.html", {"form": form})

@login_required
def dash_jobs(request):
    return render(request, "users/dash_jobs.html")

@login_required
def applications_dashboard(request):
    """Dashboard for users to view their job applications"""
    if request.user.is_organization():
        return redirect('users:dashboard')
    
    # Get filter and search parameters
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-created_at')  # Default sort by newest first
    
    # Base queryset - user's applications
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__posted_by')
    
    # Apply search filter
    if search_query:
        applications = applications.filter(
            Q(job__title__icontains=search_query) |
            Q(job__posted_by__organization_name__icontains=search_query) |
            Q(job__posted_by__username__icontains=search_query) |
            Q(job__location__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Apply sorting
    valid_sorts = [
        'created_at', '-created_at',
        'job__title', '-job__title',
        'status', '-status',
        'job__deadline', '-job__deadline'
    ]
    if sort_by in valid_sorts:
        applications = applications.order_by(sort_by)
    else:
        applications = applications.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(applications, 10)  # 10 applications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status choices for filter dropdown
    status_choices = Application.Status.choices
    
    # Statistics
    stats = {
        'total': applications.count(),
        'pending': applications.filter(status='PD').count(),
        'reviewing': applications.filter(status='RV').count(),
        'shortlisted': applications.filter(status='SL').count(),
        'selected': applications.filter(status='SE').count(),
        'rejected': applications.filter(status='RJ').count(),
        'withdrawn': applications.filter(status='WD').count(),
        'hired': applications.filter(status='HD').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'applications': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'status_choices': status_choices,
        'stats': stats,
        'current_time': timezone.now(),
    }
    
    return render(request, 'users/applications_dashboard.html', context)


@login_required
def kyc_form_view(request):
    """Render the multi-step KYC form page. The frontend JS will call API endpoints to save steps and submit."""
    # Determine which KYC type to show by user_type
    kyc_type = 'individual' if request.user.user_type == request.user.UserType.APPLICANT else 'organization'
    return render(request, 'users/kyc_form.html', {'kyc_type': kyc_type})


@staff_member_required
def cms_dashboard(request):
    """Lightweight CMS dashboard that lists Users, Jobs, Applications and KYC records with basic filters.

    Supports GET params: model (users|jobs|applications|kyc), search, status, date_from, date_to,
    user_type, registration_number, kyc_type (individual|organization).
    """
    # Simple selector to choose which table to show
    model = request.GET.get('model', 'users')
    page = int(request.GET.get('page', 1))
    per_page = 20

    # Common filters
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    user_type = request.GET.get('user_type', '').strip()
    registration_number = request.GET.get('registration_number', '').strip()
    kyc_type = request.GET.get('kyc_type', '').strip()

    context = {
        'selected': model,
        'search': search,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'user_type': user_type,
        'registration_number': registration_number,
        'kyc_type': kyc_type,
    }

    if model == 'users':
        qs = User.objects.all().order_by('-date_joined')
        if search:
            qs = qs.filter(Q(username__icontains=search) | Q(email__icontains=search))
        if user_type:
            qs = qs.filter(user_type=user_type)
        if status_filter == 'kyc_verified':
            qs = qs.filter(is_kyc_verified=True)
        elif status_filter == 'kyc_unverified':
            qs = qs.filter(is_kyc_verified=False)
        if date_from:
            qs = qs.filter(date_joined__date__gte=date_from)
        if date_to:
            qs = qs.filter(date_joined__date__lte=date_to)

        paginator = Paginator(qs, per_page)
        context['page_obj'] = paginator.get_page(page)
        context['columns'] = ['username', 'email', 'user_type', 'is_kyc_verified', 'date_joined']

    elif model == 'jobs':
        qs = Job.objects.select_related('posted_by').all().order_by('-created_at')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(posted_by__organization_name__icontains=search) | Q(posted_by__username__icontains=search))
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        paginator = Paginator(qs, per_page)
        context['page_obj'] = paginator.get_page(page)
        context['columns'] = ['title', 'posted_by', 'created_at', 'deadline']

    elif model == 'applications':
        qs = Application.objects.select_related('job', 'applicant').all().order_by('-created_at')
        if search:
            qs = qs.filter(Q(job__title__icontains=search) | Q(applicant__username__icontains=search) | Q(job__posted_by__organization_name__icontains=search))
        if status_filter:
            qs = qs.filter(status=status_filter)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        paginator = Paginator(qs, per_page)
        context['page_obj'] = paginator.get_page(page)
        context['columns'] = ['job', 'applicant', 'status', 'created_at']

    elif model == 'kyc':
        # Support filtering by type (individual/organization), status, date range, org name, registration number
        items = []
        if kyc_type in ('', 'individual'):
            ind_qs = IndividualKYC.objects.select_related('user').all().order_by('-updated_at')
            if status_filter:
                ind_qs = ind_qs.filter(status=status_filter)
            if search:
                ind_qs = ind_qs.filter(Q(full_name__icontains=search) | Q(user__username__icontains=search) | Q(citizenship_number__icontains=search))
            if date_from:
                ind_qs = ind_qs.filter(updated_at__date__gte=date_from)
            if date_to:
                ind_qs = ind_qs.filter(updated_at__date__lte=date_to)
            for k in ind_qs:
                items.append({'type': 'individual', 'id': k.id, 'user': k.user, 'status': k.status, 'updated_at': k.updated_at})

        if kyc_type in ('', 'organization'):
            org_qs = OrganizationKYC.objects.select_related('user').all().order_by('-updated_at')
            if status_filter:
                org_qs = org_qs.filter(status=status_filter)
            if search:
                org_qs = org_qs.filter(Q(org_name__icontains=search) | Q(user__username__icontains=search) | Q(registration_number__icontains=search))
            if registration_number:
                org_qs = org_qs.filter(registration_number__icontains=registration_number)
            if date_from:
                org_qs = org_qs.filter(updated_at__date__gte=date_from)
            if date_to:
                org_qs = org_qs.filter(updated_at__date__lte=date_to)
            for k in org_qs:
                items.append({'type': 'organization', 'id': k.id, 'user': k.user, 'status': k.status, 'updated_at': k.updated_at})

        items = sorted(items, key=lambda x: x['updated_at'], reverse=True)
        paginator = Paginator(items, per_page)
        context['page_obj'] = paginator.get_page(page)
        context['columns'] = ['type', 'user', 'status', 'updated_at']

    else:
        raise Http404()

    return render(request, 'cms/dashboard.html', context)
def organizations(request):
    return render(request,"users/organizations.html")
def payment(request):
    return render(request,"users/payment.html")

@login_required
@csrf_exempt
def apply_job(request):
    if request.method == "POST":
        try:
            # Check if user has completed their profile (especially for Google OAuth users)
            if request.user.user_type == User.UserType.APPLICANT and not request.user.official_name:
                return JsonResponse({
                    'error': 'Profile incomplete', 
                    'message': 'Please complete your profile before applying for jobs.',
                    'redirect_url': '/users/add-info/'
                }, status=400)
            
            data = json.loads(request.body)
            job_id = data.get('job_id')
            
            if not job_id:
                return JsonResponse({'error': 'Job ID is required'}, status=400)
                
            # Get the job object
            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return JsonResponse({'error': 'Job not found'}, status=404)
            
            # Check if user has already applied
            existing_application = Application.objects.filter(
                job=job, 
                applicant=request.user
            ).exists()
            
            if existing_application:
                return JsonResponse({'message': 'Already applied to this job'}, status=200)
            
            # Create application
            Application.objects.create(
                job=job,
                applicant=request.user,
                cover_letter="Applied via job swipe interface"
            )
            
            return JsonResponse({'message': 'Application submitted successfully'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
