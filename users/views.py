from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .forms_profile import ApplicantProfileEditForm
from .forms import ChangePasswordForm
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
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from users.models import User, IndividualKYC, OrganizationKYC, Notification, Assessment
from .decorators import applicant_required, organization_required
from organization.models import Job, Application
from django.shortcuts import Http404
from django.core.paginator import Paginator
from users.models import IndividualKYC, OrganizationKYC, KycAudit, Notification

class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        """Redirect based on user type"""
        if self.request.user.is_organization():
            return '/organization/profile/'
        else:
            return '/users/dashboard/'


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
            return redirect("home")
    else:
        form = ApplicantSignUpForm()
    return render(request, "users/job_signup.html", {"form": form})


def signup_organization(request):
    if request.method == "POST":
        form = OrganizationSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("organization:profile")
    else:
        form = OrganizationSignUpForm()
    return render(request, "users/org_signup.html", {"form": form})


@login_required
def profile(request):
    # Get user's latest assessments
    latest_assessments = Assessment.objects.filter(user=request.user).order_by('-created_at')[:3]
    
    return render(request, "users/profile.html", {
        'latest_assessments': latest_assessments
    })


def profile_detail(request, user_id):
    """View to display any user's profile (organization or applicant)"""
    user = get_object_or_404(User, id=user_id)
    
    context = {
        'profile_user': user,
    }
    
    # Add organization-specific data
    if user.is_organization():
        context['total_jobs'] = user.jobs.count()
        context['recent_jobs'] = user.jobs.order_by('-created_at')[:5]
        
        # Add follower count if OrganizationFollow model exists
        try:
            from organization.models import OrganizationFollow
            context['follower_count'] = OrganizationFollow.objects.filter(
                organization=user,
                is_active=True
            ).count()
            
            # Check if current user follows this organization
            if request.user.is_authenticated and request.user.user_type == 'APP':
                context['is_following'] = OrganizationFollow.objects.filter(
                    user=request.user,
                    organization=user,
                    is_active=True
                ).exists()
        except ImportError:
            pass
    
    return render(request, "users/profile_detail.html", context)


@login_required
def google_signup_redirect(request):
    """Redirect view for Google OAuth users"""
    user = request.user
    
    # Redirect based on user type
    if user.user_type == User.UserType.APPLICANT:
        return redirect('home')
    else:
        # If user is organization, redirect to dashboard
        return redirect('users:dashboard')


@applicant_required
def add_info(request):
    """View for Google OAuth users to complete their profile"""
    user = request.user
    
    if request.method == "POST":
        form = GoogleUserCompleteProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Profile completed successfully! You can now apply for jobs.')
            return redirect("users:dashboard")
    else:
        form = GoogleUserCompleteProfileForm(instance=user)
    
    return render(request, "users/add_info.html", {"form": form})


@applicant_required
def profile_edit(request):
    user = request.user
    if request.method == "POST":
        form = ApplicantProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("users:profile")
    else:
        form = ApplicantProfileEditForm(instance=user)
    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def change_password(request):
    """View for changing user password"""
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            try:
                # Save the new password
                user = form.save()
                
                # Refresh the user object from database to ensure changes are loaded
                user.refresh_from_db()
                
                # Update the session to keep the user logged in
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                
                # Verify password was actually changed
                if user.check_password(request.POST.get('new_password1')):
                    print(f"✅ Password successfully changed for user: {user.email}")
                    
                    # Create fresh form after successful password change
                    form = ChangePasswordForm(user)
                    
                    return render(request, "users/change_password.html", {
                        "form": form,
                        "success": True,
                        "message": "✅ Password changed successfully! Your new password is now active. You will need to use your new password for your next login."
                    })
                else:
                    print(f"❌ ERROR: Password verification failed after save for user: {user.email}")
                    raise ValueError("Password verification failed after save")
                    
            except Exception as e:
                print(f"❌ Exception during password change: {str(e)}")
                return render(request, "users/change_password.html", {
                    "form": form,
                    "success": False,
                    "error": True,
                    "error_message": f"An error occurred while changing your password: {str(e)}"
                })
        else:
            # Return form with errors
            print(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"  {field}: {error}")
            
            return render(request, "users/change_password.html", {
                "form": form,
                "success": False,
                "error": True
            })
    else:
        form = ChangePasswordForm(request.user)
    
    return render(request, "users/change_password.html", {"form": form})

@applicant_required
def dash_jobs(request):
    return render(request, "users/dash_jobs.html")

@applicant_required
def applications_dashboard(request):
    """Dashboard for users to view their job applications"""
    
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
    kyc_type = 'individual' if request.user.user_type == request.user.UserType.APPLICANT else 'organization'
    
    # Check if user already has KYC submitted/verified
    kyc_status = request.user.get_kyc_status()
    
    # Check if KYC can be edited
    can_edit = True
    edit_error = None
    
    try:
        if kyc_type == 'individual':
            kyc = IndividualKYC.objects.get(user=request.user)
        else:
            kyc = OrganizationKYC.objects.get(user=request.user)
        
        # Only allow editing if status is REJECTED or SUBMITTED
        if not kyc.is_editable():
            can_edit = False
            if kyc.status == 'VERIFIED':
                edit_error = 'Your KYC is verified. You cannot edit it.'
            elif kyc.status == 'DRAFT':
                edit_error = 'Your KYC is still in draft. Please complete and submit it first.'
    except (IndividualKYC.DoesNotExist, OrganizationKYC.DoesNotExist):
        # New KYC, allow to create
        can_edit = True
    
    # If cannot edit, show error page
    if not can_edit:
        context = {
            'kyc_type': kyc_type,
            'kyc_status': kyc_status,
            'error': edit_error,
            'can_edit': False
        }
        return render(request, 'users/kyc_form.html', context)
    
    context = {
        'kyc_type': kyc_type,
        'kyc_status': kyc_status,
        'show_banner': request.user.needs_kyc_banner(),
        'can_edit': True
    }
    return render(request, 'users/kyc_form.html', context)


@staff_member_required
@staff_member_required(login_url='/admin/login/')
def cms_dashboard(request):
    """CMS dashboard with Users, Jobs, Applications and KYC records with filters."""
    model = request.GET.get('model', 'kyc')
    page = int(request.GET.get('page', 1))
    per_page = 20

    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    user_type = request.GET.get('user_type', '').strip()
    kyc_type = request.GET.get('kyc_type', '').strip()

    context = {
        'selected': model,
        'search': search,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'user_type': user_type,
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
                items.append({'type': 'individual', 'id': k.id, 'user': k.user, 'name': k.full_name or k.user.username, 'status': k.status, 'updated_at': k.updated_at})

        if kyc_type in ('', 'organization'):
            org_qs = OrganizationKYC.objects.select_related('user').all().order_by('-updated_at')
            if status_filter:
                org_qs = org_qs.filter(status=status_filter)
            if search:
                org_qs = org_qs.filter(Q(org_name__icontains=search) | Q(user__username__icontains=search) | Q(registration_number__icontains=search))
            if date_from:
                org_qs = org_qs.filter(updated_at__date__gte=date_from)
            if date_to:
                org_qs = org_qs.filter(updated_at__date__lte=date_to)
            for k in org_qs:
                items.append({'type': 'organization', 'id': k.id, 'user': k.user, 'name': k.org_name or k.user.username, 'status': k.status, 'updated_at': k.updated_at})

        items = sorted(items, key=lambda x: x['updated_at'], reverse=True)
        paginator = Paginator(items, per_page)
        context['page_obj'] = paginator.get_page(page)
        context['columns'] = ['type', 'name', 'user', 'status', 'updated_at']

    else:
        raise Http404()

    return render(request, 'cms/dashboard.html', context)


@staff_member_required
def cms_kyc_detail(request, kyc_type, kyc_id):
    """Show full KYC details for staff and allow verify/reject actions via the admin API."""
    if kyc_type == 'individual':
        k = get_object_or_404(IndividualKYC, id=kyc_id)
    else:
        k = get_object_or_404(OrganizationKYC, id=kyc_id)

    return render(request, 'cms/kyc_detail.html', {'kyc': k, 'kyc_type': kyc_type})
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
            if request.user.user_type == User.UserType.APPLICANT and not request.user.phone:
                return JsonResponse({
                    'error': 'Profile incomplete', 
                    'message': 'Please complete your profile before applying for jobs.',
                    'redirect_url': '/users/add-info/'
                }, status=400)
            
            # KYC check: unverified users can only apply 2 jobs per day
            if not request.user.is_kyc_verified:
                if not request.user.can_apply_today():
                    return JsonResponse({
                        'error': 'Daily limit reached',
                        'message': 'Unverified users can apply to only 2 jobs per day. Complete KYC to remove this limit.',
                        'redirect_url': '/users/kyc/'
                    }, status=429)
            
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


@login_required
def kyc_profile(request):
    """Display user's KYC status and details. URL depends on user type."""
    context = {}
    
    if request.user.is_applicant():
        try:
            kyc = IndividualKYC.objects.get(user=request.user)
            context['kyc'] = kyc
            context['kyc_type'] = 'individual'
        except IndividualKYC.DoesNotExist:
            context['kyc'] = None
            context['kyc_type'] = 'individual'
    else:
        try:
            kyc = OrganizationKYC.objects.get(user=request.user)
            context['kyc'] = kyc
            context['kyc_type'] = 'organization'
        except OrganizationKYC.DoesNotExist:
            context['kyc'] = None
            context['kyc_type'] = 'organization'
    
    context['is_verified'] = request.user.is_kyc_verified
    context['title'] = 'KYC Profile'
    
    # Check if editable
    if context['kyc']:
        context['is_editable'] = context['kyc'].is_editable()
        context['edit_message'] = 'You can edit your KYC' if context['is_editable'] else 'Your KYC cannot be edited in this status'
    
    return render(request, 'users/kyc_profile.html', context)


@login_required
def notifications(request):
    """Display all user notifications with pagination and filtering"""
    all_notifications = request.user.notifications.all()
    
    # Filter by type if provided
    notif_type = request.GET.get('type', '')
    if notif_type:
        all_notifications = all_notifications.filter(notification_type=notif_type)
    
    # Filter by read/unread if provided
    read_status = request.GET.get('status', '')
    if read_status == 'unread':
        all_notifications = all_notifications.filter(is_read=False)
    elif read_status == 'read':
        all_notifications = all_notifications.filter(is_read=True)
    
    # Handle AJAX requests
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')
        
        if action == 'mark_all_read':
            all_notifications.filter(is_read=False).update(is_read=True)
            return JsonResponse({'message': 'All notifications marked as read', 'success': True})
        
        elif action == 'mark_read':
            notification_id = request.POST.get('notification_id')
            try:
                notif = Notification.objects.get(id=notification_id, user=request.user)
                notif.is_read = True
                notif.save()
                return JsonResponse({'message': 'Notification marked as read', 'success': True})
            except Notification.DoesNotExist:
                return JsonResponse({'error': 'Notification not found'}, status=404)
        
        elif action == 'delete':
            notification_id = request.POST.get('notification_id')
            try:
                notif = Notification.objects.get(id=notification_id, user=request.user)
                notif.delete()
                return JsonResponse({'message': 'Notification deleted', 'success': True})
            except Notification.DoesNotExist:
                return JsonResponse({'error': 'Notification not found'}, status=404)
        
        elif action == 'delete_all_read':
            deleted_count = request.user.notifications.filter(is_read=True).count()
            request.user.notifications.filter(is_read=True).delete()
            return JsonResponse({
                'message': f'{deleted_count} read notifications deleted',
                'success': True,
                'deleted_count': deleted_count
            })
        
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    # Pagination for GET request
    paginator = Paginator(all_notifications, 15)
    page_number = request.GET.get('page', 1)
    notifications_page = paginator.get_page(page_number)
    
    # Count unread
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    # Get notification types for filtering
    notification_types = Notification.NOTIFICATION_TYPES
    
    context = {
        'notifications': notifications_page,
        'unread_count': unread_count,
        'notification_types': notification_types,
        'current_type': notif_type,
        'current_status': read_status,
        'title': 'Notifications'
    }
    return render(request, 'users/notifications.html', context)


@login_required
def notification_count_api(request):
    """API endpoint for getting unread notification count"""
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': unread_count, 'success': True})


@login_required
def notifications_api(request):
    """API endpoint for getting recent notifications (for popup)"""
    # Get the last time the user checked notifications (from session or request)
    last_check = request.GET.get('last_check', None)
    
    if last_check:
        try:
            from datetime import datetime
            last_check_dt = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            new_notifications = request.user.notifications.filter(
                created_at__gt=last_check_dt,
                is_read=False
            ).order_by('-created_at')[:5]
        except (ValueError, TypeError):
            new_notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
    else:
        # Return latest 5 unread notifications
        new_notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
    
    notifications_data = [
        {
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'type': notif.notification_type,
            'icon': notif.get_icon(),
            'is_read': notif.is_read,
            'created_at': notif.created_at.isoformat(),
            'action_url': notif.action_url or '',
        }
        for notif in new_notifications
    ]
    
    return JsonResponse({
        'success': True,
        'notifications': notifications_data,
        'count': len(notifications_data),
        'total_unread': request.user.notifications.filter(is_read=False).count()
    })


def cms_login(request):
    """CMS login page - only for staff/superusers"""
    # If already logged in as staff, redirect to cms dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/cms/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            # Only allow staff/superusers to login to CMS
            login(request, user)
            messages.success(request, f'Welcome to CMS, {user.username}!')
            return redirect('/admin/cms/')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions. Only CMS staff can login.')
    
    return render(request, 'admin/cms_login.html')


def cms_logout(request):
    """CMS logout - redirects to CMS login page"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/admin/cms-login/')
