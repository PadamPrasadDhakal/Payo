import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobsHaruPrj.settings')
django.setup()

from organization.models import Job, Application

# Check if organization data exists
jobs = Job.objects.all()
applications = Application.objects.all()

print(f"Organization Jobs: {jobs.count()}")
print(f"Organization Applications: {applications.count()}")

if jobs.exists():
    print("\nFirst few jobs:")
    for job in jobs[:3]:
        print(f"- {job.title} by {job.posted_by}")