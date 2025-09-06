import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobsHaruPrj.settings')
django.setup()

from django.db import connection

# Copy data from jobs_job to Job table (organization uses db_table='Job')
with connection.cursor() as cursor:
    cursor.execute("""
        INSERT INTO Job (
            title, description, requirements, location, salary, 
            job_type, posted_by_id, created_at, updated_at, deadline
        )
        SELECT 
            title, description, requirements, location, salary, 
            job_type, posted_by_id, created_at, updated_at, NULL
        FROM jobs_job
        WHERE NOT EXISTS (
            SELECT 1 FROM Job WHERE Job.title = jobs_job.title AND Job.posted_by_id = jobs_job.posted_by_id
        )
    """)
    
    # Copy data from jobs_application to organization_application table
    cursor.execute("""
        INSERT INTO organization_application (
            job_id, applicant_id, cover_letter, resume, status, created_at
        )
        SELECT 
            j_new.id, ja.applicant_id, ja.cover_letter, ja.resume, ja.status, ja.created_at
        FROM jobs_application ja
        JOIN jobs_job j_old ON ja.job_id = j_old.id
        JOIN Job j_new ON j_old.title = j_new.title AND j_old.posted_by_id = j_new.posted_by_id
        WHERE NOT EXISTS (
            SELECT 1 FROM organization_application oa 
            WHERE oa.job_id = j_new.id AND oa.applicant_id = ja.applicant_id
        )
    """)

print("Data migration completed!")