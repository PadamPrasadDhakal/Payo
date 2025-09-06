from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from .forms import JobForm
from django.urls import reverse_lazy
from .models import Job, Application
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

# Create your views here.

def organization_list_view(request):
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

class JobDetailView(DetailView):
    model = Job
    context_object_name = "job"
    template_name = "organization/job_detail.html"

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

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)



