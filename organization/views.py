from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from .forms import JobForm
from django.urls import reverse_lazy
from .models import Job, Application, Payment
from django.db.models import Count, Max
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

# Create your views here.

@login_required
def organization_list_view(request):
    # Only allow logged-in organizations to view their jobs list
    org = request.user
    jobs = Job.objects.filter(posted_by=org).order_by('-created_at')[:3]
    for job in jobs:
        job.app_count = job.applications.count()
        job.status = 'Accepting' if job.deadline is None or job.deadline > timezone.now() else 'Pending'
    return render(request, "organization/organization_list.html", {"jobs": jobs})


@method_decorator(login_required, name='dispatch')
class JobListView(ListView):
    model = Job
    context_object_name = "jobs"
    template_name = "organization/job_list.html"
    paginate_by = 20

    def get_queryset(self):
        # Only show jobs posted by the logged-in organization
        return Job.objects.filter(posted_by=self.request.user).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class JobDetailView(DetailView):
    model = Job
    context_object_name = "job"
    template_name = "organization/job_detail.html"
    
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

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)

@login_required
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

@login_required
def applications_overview(request):
    jobs = (
        Job.objects.filter(posted_by=request.user)
        .annotate(total_applications=Count("applications"), opened_at=Max("created_at"))
        .order_by("-created_at")
    )
    return render(request, "organization/applications.html", {"jobs": jobs})

@login_required
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

@login_required
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


@login_required
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
    
    context = {
        'jobs_count': jobs_count,
        'applications_count': applications_count,
        'recent_jobs': recent_jobs,
        'recent_payments': recent_payments,
        'active_subscription': active_subscription,
    }
    
    return render(request, "organization/org_profile.html", context)

@login_required
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
        # Check if organization has completed KYC
        if not request.user.can_post_jobs():
            from django.contrib import messages
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


@login_required
def payment_page(request):
    """Payment page for organizations to purchase plans"""
    # Only organizations can access this page
    if not request.user.is_organization:
        messages.error(request, 'Only organizations can purchase plans.')
        return redirect('organization:pricing')
    
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


@login_required
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
            transaction_id=f"TXN_{request.user.id}_{plan}_{timezone.now().timestamp()}"
        )
        
        # Here you would integrate with actual payment gateway (Esewa, Khalti, Stripe)
        # For now, we'll mark as completed
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        
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


@login_required
def org_profile_edit(request):
    """Edit organization profile"""
    # Ensure only organizations can access this
    if not request.user.is_organization():
        return redirect('organization:profile')
    
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

