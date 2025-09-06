from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy

from organization.models import Job, Application


class JobListView(ListView):
    model = Job
    context_object_name = "jobs"
    template_name = "jobs/job_list.html"
    paginate_by = 20


class JobDetailView(DetailView):
    model = Job
    context_object_name = "job"
    template_name = "jobs/job_detail.html"


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
