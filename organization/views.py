from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from .forms import JobForm
from django.urls import reverse_lazy
from .models import Job, Application, Payment, OrganizationFollow
from django.db.models import Count, Max, Q, Exists, OuterRef
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.contrib import messages
from users.decorators import organization_required, applicant_required
from users.models import User
from django.core.paginator import Paginator
from django.db.models.functions import Lower

# Create your views here.

@organization_required
def organization_list_view(request):
    # Only allow logged-in organizations to view their jobs list
    org = request.user
    jobs = Job.objects.filter(posted_by=org).order_by('-created_at')[:3]
    for job in jobs:
        job.app_count = job.applications.count()
        job.status = 'Accepting' if job.deadline is None or job.deadline > timezone.now() else 'Pending'
    return render(request, "organization/organization_list.html", {"jobs": jobs})


class JobListView(LoginRequiredMixin, ListView):
    model = Job
    context_object_name = "jobs"
    template_name = "organization/job_list.html"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'ORG':
            messages.warning(request, "⚠️ You don't have permission to access this page. This page is for organizations only.")
            return redirect('/users/profile/')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Only show jobs posted by the logged-in organization
        return Job.objects.filter(posted_by=self.request.user).order_by('-created_at')

class JobDetailView(LoginRequiredMixin, DetailView):
    model = Job
    context_object_name = "job"
    template_name = "organization/job_detail.html"
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'ORG':
            messages.warning(request, "⚠️ You don't have permission to access this page. This page is for organizations only.")
            return redirect('/users/profile/')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        job = super().get_object()
        # Ensure the job belongs to the logged-in organization
        if job.posted_by != self.request.user:
            from django.http import Http404
            raise Http404("Job not found")
        return job
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.object
        # Add applications with related user data
        applications = job.applications.select_related('applicant').order_by('-created_at')
        context['applications'] = applications
        context['applications_count'] = applications.count()
        return context

class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    fields = ["title", "description", "requirements", "location", "salary", "job_type"]
    template_name = "organization/post_job.html"
    success_url = reverse_lazy("organization:job-list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'ORG':
            messages.warning(request, "⚠️ You don't have permission to access this page. This page is for organizations only.")
            return redirect('/users/profile/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)

@applicant_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    error = None
    if request.method == "POST":
        cover_letter = request.POST.get("cover_letter", "").strip()
        resume = request.FILES.get("resume")
        if not cover_letter or not resume:
            error = "All fields are required."
        else:
            Application.objects.get_or_create(
                job=job,
                applicant=request.user,
                defaults={"cover_letter": cover_letter, "resume": resume},
            )
            return redirect("organization:job-detail", pk=pk)
    return render(request, "organization/apply_job.html", {"job": job, "error": error})

@organization_required
def applications_overview(request):
    jobs = (
        Job.objects.filter(posted_by=request.user)
        .annotate(total_applications=Count("applications"), opened_at=Max("created_at"))
        .order_by("-created_at")
    )
    return render(request, "organization/applications.html", {"jobs": jobs})

@organization_required
def application_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    applicants = job.applications.select_related("applicant").order_by("-created_at")
    context = {
        "job": job,
        "deadline": job.deadline,
        "applicant_count": applicants.count(),
        "applicants": applicants,
    }
    return render(request, "organization/application_details.html", context)


# download stopwords once (put in your setup, not inside function)
nltk.download("stopwords", quiet=True)
stop_words = set(stopwords.words("english"))

nltk.download("stopwords", quiet=True)
stop_words = set(stopwords.words("english"))

def classify(resume_pdfs, job_descriptions):
    """
    Compare multiple resumes against one or more job descriptions.

    Args:
        resume_pdfs (list): List of resume PDF file paths
        job_descriptions (str | list): Either a single job description (string) 
                                       or multiple job descriptions (list of strings)

    Returns:
        dict: {resume -> {job -> score}}
    """

    # ---- extract text from PDF ----
    def extract_text_from_pdf(pdf_path):
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        return text

    # ---- preprocess ----
    def preprocess_text(text):
        text = text.lower()
        text = re.sub(r"[^a-z\s]", "", text)
        words = [w for w in text.split() if w not in stop_words]
        return " ".join(words)

    # ---- Handle resumes ----
    resume_texts = [preprocess_text(extract_text_from_pdf(r)) for r in resume_pdfs]

    # ---- Handle jobs (string or list) ----
    if isinstance(job_descriptions, str):
        job_texts = [preprocess_text(job_descriptions)]
    else:
        job_texts = [preprocess_text(j) for j in job_descriptions]

    # ---- Vectorize all documents ----
    documents = resume_texts + job_texts
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # ---- Compare each resume with each job ----
    similarities = cosine_similarity(tfidf_matrix[:len(resume_texts)], 
                                     tfidf_matrix[len(resume_texts):])

    results = {}
    for i, resume in enumerate(resume_pdfs):
        results[resume] = {}
        for j, job in enumerate(job_descriptions if isinstance(job_descriptions, list) else [job_descriptions]):
            results[resume][job] = float(similarities[i][j])

    return results



def match_resumes(request):
    resumes = [
        "media/resumes/pratik_acharya.pdf",
    ]
    job =  ["Looking for Python Django Developer", "Hiring Data Analyst with SQL and Excel","Accountant with financial reporting skills"]

    results = classify(resumes, job)

    # Send results to demo.html
    return render(request, "demo.html", {"results": results})

@organization_required
def org_dashboard(request):
    org = request.user
    jobs = Job.objects.filter(posted_by=org).order_by('-created_at')
    applications_by_job = {job: job.applications.count() for job in jobs}
    job_count = jobs.count()
    return render(request, "organization/dashboard.html", {
        "jobs": jobs,
        "applications_by_job": applications_by_job,
        "job_count": job_count,
    })


@organization_required
def org_profile(request):
    """Organization profile view"""
    if not request.user.is_organization:
        messages.error(request, 'Only organizations can access this page.')
        return redirect('/')
    
    org = request.user
    
    # Get statistics
    jobs_count = Job.objects.filter(posted_by=org).count()
    applications_count = Application.objects.filter(job__posted_by=org).count()
    
    # Get 3 most recent active job postings
    recent_jobs = Job.objects.filter(posted_by=org).order_by('-created_at')[:3]
    
    # Get recent payments
    recent_payments = Payment.objects.filter(organization=org).order_by('-created_at')[:5]
    
    # Get active subscription
    active_subscription = Payment.objects.filter(
        organization=org,
        status='completed'
    ).order_by('-subscription_end').first()
    
    # Get latest payment with premium approval status
    latest_payment = Payment.objects.filter(organization=org).order_by('-created_at').first()
    is_premium_approved = latest_payment and latest_payment.premium_status == 'approved'
    premium_status = latest_payment.premium_status if latest_payment else None
    
    context = {
        'jobs_count': jobs_count,
        'applications_count': applications_count,
        'recent_jobs': recent_jobs,
        'recent_payments': recent_payments,
        'active_subscription': active_subscription,
        'is_premium_approved': is_premium_approved,
        'premium_status': premium_status,
        'latest_payment': latest_payment,
    }
    
    return render(request, "organization/org_profile.html", context)

@organization_required
def org_jobs(request):
    org = request.user
    jobs = Job.objects.filter(posted_by=org).order_by('-created_at')
    job_count = jobs.count()
    return render(request, "organization/org_jobs.html", {"jobs": jobs, "job_count": job_count})

class OrgJobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = "organization/post_job.html"
    success_url = reverse_lazy("organization:job-list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'ORG':
            messages.warning(request, "⚠️ You don't have permission to access this page. This page is for organizations only.")
            return redirect('/users/profile/')
        # Check if organization has completed KYC
        if not request.user.can_post_jobs():
            messages.error(request, 'Please complete KYC verification to post jobs.')
            return redirect('/users/kyc/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)


@login_required
@csrf_exempt
@require_POST
def update_application_status(request):
    """Update application status with optional notes"""
    try:
        data = json.loads(request.body)
        application_id = data.get('application_id')
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        if not application_id or not new_status:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Get application and verify organization owns the job
        application = get_object_or_404(Application, id=application_id)
        if application.job.posted_by != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Validate status
        valid_statuses = [choice[0] for choice in Application.Status.choices]
        if new_status not in valid_statuses:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        # Update application
        old_status = application.status
        application.status = new_status
        # Always update reviewed_at for ALL status changes to ensure notifications work
        application.reviewed_at = timezone.now()
        if notes:
            application.notes = notes
        else:
            # Add default note for tracking
            application.notes = f"Status changed from {application.get_status_display()} to {dict(Application.Status.choices)[new_status]} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        application.save()
        
        # Update profile achievements for boosting (regardless of final outcome)
        applicant = application.applicant
        if applicant.is_applicant():
            # Only increment if this is a new achievement (prevent double counting)
            if old_status != new_status:
                if new_status == 'SL' and old_status not in ['SL', 'SE', 'HD']:  # First time shortlisted
                    applicant.increment_achievement('shortlisted')
                elif new_status == 'SE' and old_status not in ['SE', 'HD']:  # First time selected
                    applicant.increment_achievement('selected')
                elif new_status == 'HD' and old_status != 'HD':  # First time hired
                    applicant.increment_achievement('hired')
        
        # Create notifications for applicant based on status change
        from users.models import Notification
        
        notification_configs = {
            'SL': {
                'type': 'APP_SHORTLISTED',
                'title': '🎯 You\'ve been Shortlisted!',
                'message': f'Great news! You\'ve been shortlisted for the position of {application.job.title} at {application.job.posted_by.organization_name or "the company"}.',
            },
            'SE': {
                'type': 'APP_SELECTED',
                'title': '🎉 You\'ve been Selected!',
                'message': f'Congratulations! You\'ve been selected for {application.job.title} at {application.job.posted_by.organization_name or "the company"}. They will contact you soon.',
            },
            'HD': {
                'type': 'APP_HIRED',
                'title': '🎊 You\'re Hired!',
                'message': f'Amazing! You\'ve been hired for {application.job.title} at {application.job.posted_by.organization_name or "the company"}. Welcome aboard!',
            },
            'RJ': {
                'type': 'APP_REJECTED',
                'title': 'Application Update',
                'message': f'Your application for {application.job.title} was not successful this time. Keep applying - the right opportunity is waiting for you!',
            },
            'RV': {
                'type': 'APP_REVIEWED',
                'title': '👀 Application Under Review',
                'message': f'Your application for {application.job.title} is now being reviewed by {application.job.posted_by.organization_name or "the organization"}.',
            },
        }
        
        # Only send notification if status actually changed
        if old_status != new_status and new_status in notification_configs:
            config = notification_configs[new_status]
            Notification.objects.create(
                user=applicant,
                title=config['title'],
                message=config['message'],
                notification_type=config['type'],
                related_id=application.id,
                action_url=f'/users/applications/?highlight={application.id}'
            )
        
        # Log the update for debugging
        print(f"Status updated for application {application.id}: {old_status} -> {new_status} at {application.reviewed_at}")
        
        return JsonResponse({
            'success': True,
            'message': f'Application status updated to {application.get_status_display()}',
            'old_status': old_status,
            'new_status': new_status,
            'status_display': application.get_status_display(),
            'status_color': application.get_status_color()
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@organization_required
def payment_page(request):
    """Payment page for organizations to purchase plans"""
    # Check if organization has completed KYC verification (MANDATORY)
    if not request.user.is_kyc_verified:
        messages.error(request, 'KYC verification is mandatory before making payments. Please complete your KYC first.')
        return redirect('users:kyc-verify')  # or appropriate KYC URL
    
    plan = request.GET.get('plan', 'growth')
    
    # Validate plan
    valid_plans = ['starter', 'growth', 'enterprise']
    if plan not in valid_plans:
        plan = 'growth'
    
    # Get plan details
    plan_details = {
        'starter': {
            'name': 'Starter Plan',
            'price': 1000,
            'description': 'Perfect for small teams and startups',
            'features': ['Up to 50 job postings', 'Basic analytics', 'Email support']
        },
        'growth': {
            'name': 'Growth Plan',
            'price': 3000,
            'description': 'Ideal for growing companies',
            'features': ['Unlimited job postings', 'Advanced analytics', 'Priority support', 'AI screening']
        },
        'enterprise': {
            'name': 'Enterprise Plan',
            'price': 7000,
            'description': 'For large organizations',
            'features': ['Everything in Growth', 'Custom integrations', 'Dedicated account manager', '24/7 support']
        }
    }
    
    selected_plan = plan_details.get(plan, plan_details['growth'])
    
    context = {
        'plan': plan,
        'selected_plan': selected_plan,
        'all_plans': plan_details,
    }
    
    return render(request, 'organization/payment.html', context)


@organization_required
def process_payment(request):
    """Process payment submission"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
    if not request.user.is_organization:
        return JsonResponse({'success': False, 'error': 'Only organizations can make payments'}, status=403)
    
    try:
        data = json.loads(request.body)
        plan = data.get('plan')
        payment_method = data.get('payment_method')
        
        # Validate plan
        valid_plans = ['starter', 'growth', 'enterprise']
        if plan not in valid_plans:
            return JsonResponse({'success': False, 'error': 'Invalid plan'}, status=400)
        
        # Validate payment method
        valid_methods = ['esewa', 'khalti', 'credit_card']
        if payment_method not in valid_methods:
            return JsonResponse({'success': False, 'error': 'Invalid payment method'}, status=400)
        
        # Get payment details based on method
        if payment_method == 'credit_card':
            card_number = data.get('card_number', '').strip()
            card_expiry = data.get('card_expiry', '').strip()
            card_cvv = data.get('card_cvv', '').strip()
            
            # Basic validation
            if not card_number or not card_expiry or not card_cvv:
                return JsonResponse({'success': False, 'error': 'All credit card fields are required'}, status=400)
            
            if len(card_number) < 13:
                return JsonResponse({'success': False, 'error': 'Invalid card number'}, status=400)
        
        else:  # esewa or khalti
            user_id = data.get('user_id', '').strip()
            password = data.get('password', '').strip()
            
            if not user_id or not password:
                return JsonResponse({'success': False, 'error': f'{payment_method.capitalize()} ID and password are required'}, status=400)
        
        # Get plan price
        prices = {'starter': 1000, 'growth': 3000, 'enterprise': 7000}
        amount = prices.get(plan, 0)
        
        # Create payment record
        payment = Payment.objects.create(
            organization=request.user,
            plan=plan,
            amount=amount,
            payment_method=payment_method,
            status='pending',
            premium_status='pending',  # Set to pending for admin review
            transaction_id=f"TXN_{request.user.id}_{plan}_{timezone.now().timestamp()}"
        )
        
        # Here you would integrate with actual payment gateway (Esewa, Khalti, Stripe)
        # For now, we'll mark as completed
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        payment.premium_status = 'pending'  # Awaiting admin approval
        
        # Set subscription dates
        from datetime import timedelta
        payment.subscription_start = timezone.now()
        payment.subscription_end = timezone.now() + timedelta(days=30)  # 1 month subscription
        
        payment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Payment completed successfully!',
            'payment_id': payment.id,
            'redirect': '/organization/dashboard/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@organization_required
def org_profile_edit(request):
    """Edit organization profile"""
    org = request.user
    
    if request.method == 'POST':
        from .forms import OrganizationProfileEditForm
        form = OrganizationProfileEditForm(request.POST, request.FILES, instance=org)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organization profile updated successfully!')
            return redirect('organization:profile')
    else:
        from .forms import OrganizationProfileEditForm
        form = OrganizationProfileEditForm(instance=org)
    
    context = {
        'form': form,
        'org': org,
    }
    return render(request, 'organization/org_profile_edit.html', context)


@login_required
@require_POST
def approve_premium(request):
    """API endpoint for admins to approve premium requests (requires admin permission)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        
        if not payment_id:
            return JsonResponse({'success': False, 'error': 'Missing payment_id'}, status=400)
        
        payment = get_object_or_404(Payment, id=payment_id)
        
        # Update premium status
        payment.premium_status = 'approved'
        payment.premium_approved_at = timezone.now()
        payment.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Premium approved for {payment.organization.username}',
            'payment_id': payment.id,
            'premium_status': payment.premium_status
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def reject_premium(request):
    """API endpoint for admins to reject premium requests (requires admin permission)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        reason = data.get('reason', 'No reason provided')
        
        if not payment_id:
            return JsonResponse({'success': False, 'error': 'Missing payment_id'}, status=400)
        
        payment = get_object_or_404(Payment, id=payment_id)
        
        # Update premium status
        payment.premium_status = 'rejected'
        payment.save()
        
        # Create rejection notification for organization
        from users.models import Notification
        Notification.objects.create(
            user=payment.organization,
            title='Premium Request Rejected',
            message=f'Your premium request for {payment.get_plan_display_name()} has been rejected. Reason: {reason}',
            notification_type='GENERAL'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Premium rejected for {payment.organization.username}',
            'payment_id': payment.id,
            'premium_status': payment.premium_status
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== TOP USERS FEATURE ====================

@organization_required
def top_users_list(request):
    """Display top-ranked users filtered by organization's industry"""
    org = request.user
    
    # Check if organization has set their industry
    if not org.organization_industry:
        messages.warning(request, "Please complete your organization profile and set your industry to view top users.")
        return redirect('organization:profile-edit')
    
    # Get filter parameters
    limit = int(request.GET.get('limit', 25))
    experience_level = request.GET.get('experience_level', '')
    skills_filter = request.GET.get('skills', '')
    location_filter = request.GET.get('location', '')
    min_rating = request.GET.get('min_rating', '')
    
    # Base queryset - try to filter by matching industry first
    from users.models import User
    users = User.objects.filter(
        user_type=User.UserType.APPLICANT,
        industry_field=org.organization_industry
    ).select_related().order_by('-employee_ranking')
    
    # If no users in organization's industry, show all users ordered by rating
    if not users.exists():
        users = User.objects.filter(
            user_type=User.UserType.APPLICANT
        ).select_related().order_by('-profile_score')
        messages.info(request, "No users found in your industry. Showing all top users across all industries.")
    
    # Apply filters
    if experience_level:
        users = users.filter(experience_level=experience_level)
    
    if skills_filter:
        users = users.filter(skills__icontains=skills_filter)
    
    if location_filter:
        users = users.filter(address__icontains=location_filter)
    
    if min_rating:
        try:
            min_rating_val = float(min_rating)
            # Calculate rating from profile_score (divide by 100, max 5.0)
            min_score = min(min_rating_val * 100, 500)
            users = users.filter(profile_score__gte=min_score)
        except ValueError:
            pass
    
    # Limit results
    users_list = list(users[:limit])
    
    # Add calculated rating to each user (profile_score / 100, max 5.0)
    for user in users_list:
        user.calculated_rating = min(user.profile_score / 100, 5.0)
    
    # Get available experience levels for filter dropdown
    experience_levels = [
        ('entry', 'Entry Level'),
        ('intermediate', 'Intermediate'),
        ('senior', 'Senior'),
        ('expert', 'Expert')
    ]
    
    context = {
        'users': users_list,
        'experience_levels': experience_levels,
        'current_filters': {
            'limit': limit,
            'experience_level': experience_level,
            'skills': skills_filter,
            'location': location_filter,
            'min_rating': min_rating,
        }
    }
    
    return render(request, 'organization/top_users_list.html', context)


@organization_required
def top_user_detail(request, user_id):
    """Display detailed profile of a top user (no resume access)"""
    from users.models import User
    
    # Get the user profile
    profile_user = get_object_or_404(User, id=user_id, user_type=User.UserType.APPLICANT)
    
    # Add calculated rating (profile_score / 100, max 5.0)
    profile_user.calculated_rating = min(profile_user.profile_score / 100, 5.0)
    
    # Check if user belongs to organization's industry (optional check, allow all if no match)
    # if profile_user.industry_field != request.user.organization_industry:
    #     messages.warning(request, "This user is not in your organization's industry.")
    #     return redirect('organization:top-users')
    
    context = {
        'profile_user': profile_user,
    }
    
    return render(request, 'organization/top_user_detail.html', context)


@organization_required
@require_POST
def express_interest(request, user_id):
    """Allow organization to express interest in a top user"""
    from users.models import User, Notification
    
    profile_user = get_object_or_404(User, id=user_id, user_type=User.UserType.APPLICANT)
    
    # Create notification for the user
    Notification.objects.create(
        user=profile_user,
        title='Organization Interested in Your Profile',
        message=f'{request.user.organization_name or request.user.username} has expressed interest in your profile. They may reach out with opportunities!',
        notification_type='GENERAL'
    )
    
    # Create notification for organization (confirmation)
    messages.success(request, f"Interest expressed in {profile_user.get_full_name() or profile_user.username}'s profile!")
    
    return JsonResponse({
        'success': True,
        'message': 'Interest expressed successfully!'
    })


# ==================== ORGANIZATION FOLLOW SYSTEM VIEWS ====================

def organizations_directory(request):
    """
    Display all organizations in a directory/list view.
    Accessible to both logged-in and logged-out users (applicants only).
    Organizations trying to access this page will be redirected.
    """
    # Check if user is an organization and redirect them
    if request.user.is_authenticated and request.user.user_type == 'ORG':
        messages.warning(request, "⚠️ Organizations cannot access the organizations directory. This feature is for job seekers only.")
        return redirect('org_dashboard')
    
    # Get all organization users
    organizations = User.objects.filter(user_type='ORG')
    
    # Annotate with follower count
    organizations = organizations.annotate(
        follower_count=Count('followers', filter=Q(followers__is_active=True))
    )
    
    # If user is logged in and is an applicant, annotate with follow status
    if request.user.is_authenticated and request.user.user_type == 'APP':
        organizations = organizations.annotate(
            is_followed=Exists(
                OrganizationFollow.objects.filter(
                    user=request.user,
                    organization=OuterRef('pk'),
                    is_active=True
                )
            )
        )
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        organizations = organizations.filter(
            Q(organization_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(organization_industry__icontains=search_query)
        )
    
    # Filter by industry
    industry_filter = request.GET.get('industry', '').strip()
    if industry_filter:
        organizations = organizations.filter(organization_industry__iexact=industry_filter)
    
    # Filter by location
    location_filter = request.GET.get('location', '').strip()
    if location_filter:
        organizations = organizations.filter(address__icontains=location_filter)
    
    # Get distinct industries and locations for filter options
    all_industries = User.objects.filter(
        user_type='ORG', 
        organization_industry__isnull=False
    ).exclude(organization_industry='').values_list(
        'organization_industry', flat=True
    ).distinct().order_by('organization_industry')
    
    all_locations = User.objects.filter(
        user_type='ORG',
        address__isnull=False
    ).exclude(address='').values_list(
        'address', flat=True
    ).distinct().order_by('address')
    
    # Order by follower count (most followed first), then by name
    organizations = organizations.order_by('-follower_count', 'organization_name')
    
    # Pagination - 20 organizations per page
    paginator = Paginator(organizations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'organizations': page_obj.object_list,
        'search_query': search_query,
        'industry_filter': industry_filter,
        'location_filter': location_filter,
        'all_industries': all_industries,
        'all_locations': all_locations,
        'total_count': paginator.count,
    }
    
    return render(request, 'organization/organizations_directory.html', context)


@login_required
@require_POST
def follow_organization(request, org_id):
    """
    Follow an organization (AJAX endpoint).
    Only applicants can follow organizations.
    """
    # Check if user is an applicant
    if request.user.user_type != 'APP':
        return JsonResponse({
            'success': False,
            'error': 'Only job seekers can follow organizations.'
        }, status=403)
    
    # Get the organization
    try:
        organization = User.objects.get(id=org_id, user_type='ORG')
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Organization not found.'
        }, status=404)
    
    # Check if already following
    existing_follow = OrganizationFollow.objects.filter(
        user=request.user,
        organization=organization
    ).first()
    
    if existing_follow:
        if existing_follow.is_active:
            return JsonResponse({
                'success': False,
                'error': 'You are already following this organization.'
            }, status=400)
        else:
            # Reactivate the follow
            existing_follow.is_active = True
            existing_follow.followed_at = timezone.now()
            existing_follow.save()
    else:
        # Create new follow relationship
        OrganizationFollow.objects.create(
            user=request.user,
            organization=organization,
            is_active=True
        )
    
    # Get updated follower count
    follower_count = OrganizationFollow.objects.filter(
        organization=organization,
        is_active=True
    ).count()
    
    messages.success(request, f'✓ You are now following {organization.organization_name or organization.username}!')
    
    return JsonResponse({
        'success': True,
        'message': f'You are now following {organization.organization_name or organization.username}',
        'follower_count': follower_count,
        'is_following': True
    })


@login_required
@require_POST
def unfollow_organization(request, org_id):
    """
    Unfollow an organization (AJAX endpoint).
    Only applicants can unfollow organizations.
    """
    # Check if user is an applicant
    if request.user.user_type != 'APP':
        return JsonResponse({
            'success': False,
            'error': 'Only job seekers can unfollow organizations.'
        }, status=403)
    
    # Get the organization
    try:
        organization = User.objects.get(id=org_id, user_type='ORG')
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Organization not found.'
        }, status=404)
    
    # Get the follow relationship
    try:
        follow = OrganizationFollow.objects.get(
            user=request.user,
            organization=organization,
            is_active=True
        )
        # Deactivate instead of delete to maintain history
        follow.is_active = False
        follow.save()
        
        # Get updated follower count
        follower_count = OrganizationFollow.objects.filter(
            organization=organization,
            is_active=True
        ).count()
        
        messages.success(request, f'You have unfollowed {organization.organization_name or organization.username}')
        
        return JsonResponse({
            'success': True,
            'message': f'You have unfollowed {organization.organization_name or organization.username}',
            'follower_count': follower_count,
            'is_following': False
        })
        
    except OrganizationFollow.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'You are not following this organization.'
        }, status=400)
