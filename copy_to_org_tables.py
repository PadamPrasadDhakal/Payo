import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobsHaruPrj.settings')
django.setup()

from django.db import connection

# Create organization tables and copy data
with connection.cursor() as cursor:
    # Create organization_job table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organization_job (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT,
            location VARCHAR(255),
            salary VARCHAR(255),
            job_type VARCHAR(2) NOT NULL DEFAULT 'FT',
            posted_by_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            deadline DATETIME,
            FOREIGN KEY (posted_by_id) REFERENCES users_user (id)
        )
    """)
    
    # Create organization_application table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organization_application (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            applicant_id INTEGER NOT NULL,
            cover_letter TEXT,
            resume VARCHAR(100),
            status VARCHAR(2) NOT NULL DEFAULT 'AP',
            created_at DATETIME NOT NULL,
            FOREIGN KEY (job_id) REFERENCES organization_job (id),
            FOREIGN KEY (applicant_id) REFERENCES users_user (id),
            UNIQUE (job_id, applicant_id)
        )
    """)
    
    # Copy data from jobs_job to organization_job
    cursor.execute("""
        INSERT OR IGNORE INTO organization_job (
            title, description, requirements, location, salary, 
            job_type, posted_by_id, created_at, updated_at, deadline
        )
        SELECT 
            title, description, requirements, location, salary, 
            job_type, posted_by_id, created_at, updated_at, NULL
        FROM jobs_job
    """)
    
    # Copy data from jobs_application to organization_application
    cursor.execute("""
        INSERT OR IGNORE INTO organization_application (
            job_id, applicant_id, cover_letter, resume, status, created_at
        )
        SELECT 
            oj.id, ja.applicant_id, ja.cover_letter, ja.resume, ja.status, ja.created_at
        FROM jobs_application ja
        JOIN jobs_job jj ON ja.job_id = jj.id
        JOIN organization_job oj ON jj.title = oj.title AND jj.posted_by_id = oj.posted_by_id
    """)

print("Organization tables created and data copied successfully!")