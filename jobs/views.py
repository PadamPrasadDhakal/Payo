from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.db.models import Q, Exists, OuterRef, Case, When, IntegerField, BooleanField
from organization.models import Job, Application, OrganizationFollow


class JobListView(ListView):
    model = Job
    context_object_name = "jobs"
    template_name = "jobs/job_list.html"
    paginate_by = 20
    
    def get_queryset(self):
        """
        Get job queryset with prioritization for followed organizations.
        If user is authenticated and is an applicant, show followed org jobs first.
        EXCLUDES internships (job_type='IN') - they appear on the Internships page.
        """
        # Exclude internships from the jobs list
        queryset = Job.objects.select_related('posted_by').exclude(job_type='IN')
        
        # Check if user is authenticated and is an applicant
        if self.request.user.is_authenticated and self.request.user.user_type == 'APP':
            # Annotate jobs with whether they're from a followed organization
            queryset = queryset.annotate(
                is_followed_org=Exists(
                    OrganizationFollow.objects.filter(
                        user=self.request.user,
                        organization=OuterRef('posted_by'),
                        is_active=True
                    )
                )
            )
            # Order by: followed orgs first, then by creation date (newest first)
            queryset = queryset.order_by('-is_followed_org', '-created_at')
        else:
            # For non-authenticated or organization users, just order by date
            queryset = queryset.order_by('-created_at')
        
        # Apply search filter
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(posted_by__organization_name__icontains=search_query)
            )
        
        # Apply location filter
        location = self.request.GET.get('location', '').strip()
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Apply job type filter (but still exclude internships)
        job_type = self.request.GET.get('job_type', '').strip()
        if job_type and job_type != 'IN':  # Don't allow filtering to show internships
            queryset = queryset.filter(job_type=job_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter parameters to context for template
        context['search_query'] = self.request.GET.get('search', '')
        context['location_filter'] = self.request.GET.get('location', '')
        context['job_type_filter'] = self.request.GET.get('job_type', '')
        
        # Add followed organization IDs for JavaScript to know which orgs are followed
        if self.request.user.is_authenticated and self.request.user.user_type == 'APP':
            followed_org_ids = OrganizationFollow.objects.filter(
                user=self.request.user,
                is_active=True
            ).values_list('organization_id', flat=True)
            context['followed_org_ids'] = list(followed_org_ids)
        else:
            context['followed_org_ids'] = []
        
        return context


class JobDetailView(DetailView):
    model = Job
    context_object_name = "job"
    template_name = "jobs/job_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if current user is following the organization that posted this job
        if self.request.user.is_authenticated and self.request.user.user_type == 'APP':
            is_following = OrganizationFollow.objects.filter(
                user=self.request.user,
                organization=self.object.posted_by,
                is_active=True
            ).exists()
            context['is_following_org'] = is_following
        else:
            context['is_following_org'] = False
        
        return context


class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    fields = [
        "title",
        "description",
        "requirements",
        "location",
        "salary",
        "job_type",
    ]
    template_name = "jobs/post_job.html"
    success_url = reverse_lazy("jobs:list")

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
            return redirect("jobs:detail", pk=pk)
    return render(request, "jobs/apply_job.html", {"job": job, "error": error})

from django.shortcuts import render

# Create your views here.
