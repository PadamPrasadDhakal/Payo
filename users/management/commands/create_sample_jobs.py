from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from organization.models import Job

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample jobs for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of sample jobs to create (default: 5)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get or create an organization user to post jobs
        org_user, created = User.objects.get_or_create(
            username='sample_org',
            defaults={
                'user_type': User.UserType.ORGANIZATION,
                'organization_name': 'Sample Company Ltd.',
                'email': 'hr@samplecompany.com',
                'first_name': 'HR',
                'last_name': 'Department'
            }
        )
        
        if created:
            org_user.set_password('password123')
            org_user.save()
            self.stdout.write(f'Created organization user: {org_user.username}')
        
        # Sample job data
        sample_jobs = [
            {
                'title': 'Software Developer',
                'description': 'We are looking for a skilled software developer to join our team. You will be responsible for developing web applications using Django and React.',
                'location': 'Kathmandu, Nepal',
                'salary': '50000',
                'job_type': 'FT',
                'skills': 'Python, Django, React, JavaScript, PostgreSQL'
            },
            {
                'title': 'Digital Marketing Specialist',
                'description': 'Join our marketing team to create and execute digital marketing campaigns. Experience with social media marketing and SEO required.',
                'location': 'Pokhara, Nepal',
                'salary': '35000',
                'job_type': 'FT',
                'skills': 'Digital Marketing, SEO, Social Media, Google Analytics'
            },
            {
                'title': 'Graphic Designer',
                'description': 'Creative graphic designer needed for designing marketing materials, websites, and brand assets. Portfolio required.',
                'location': 'Lalitpur, Nepal',
                'salary': '30000',
                'job_type': 'PT',
                'skills': 'Adobe Photoshop, Illustrator, InDesign, Figma'
            },
            {
                'title': 'Data Analyst',
                'description': 'Analyze business data to provide insights and recommendations. Experience with Python, SQL, and data visualization tools preferred.',
                'location': 'Bhaktapur, Nepal',
                'salary': '45000',
                'job_type': 'FT',
                'skills': 'Python, SQL, Excel, Power BI, Statistics'
            },
            {
                'title': 'Content Writer',
                'description': 'Create engaging content for websites, blogs, and social media. Excellent writing skills and SEO knowledge required.',
                'location': 'Remote',
                'salary': '25000',
                'job_type': 'PT',
                'skills': 'Content Writing, SEO, WordPress, Research'
            },
            {
                'title': 'Customer Service Representative',
                'description': 'Provide excellent customer service via phone, email, and chat. Good communication skills essential.',
                'location': 'Kathmandu, Nepal',
                'salary': '20000',
                'job_type': 'FT',
                'skills': 'Communication, Customer Service, Problem Solving'
            },
            {
                'title': 'Sales Executive',
                'description': 'Drive sales growth by identifying and pursuing new business opportunities. Previous sales experience preferred.',
                'location': 'Chitwan, Nepal',
                'salary': '40000',
                'job_type': 'FT',
                'skills': 'Sales, Negotiation, Lead Generation, CRM'
            }
        ]
        
        created_jobs = 0
        for i in range(min(count, len(sample_jobs))):
            job_data = sample_jobs[i % len(sample_jobs)]
            
            job, created = Job.objects.get_or_create(
                title=f"{job_data['title']} #{i+1}",
                posted_by=org_user,
                defaults={
                    **job_data,
                    'title': f"{job_data['title']} #{i+1}"
                }
            )
            
            if created:
                created_jobs += 1
                self.stdout.write(f'Created job: {job.title}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_jobs} new jobs')
        )
        
        total_jobs = Job.objects.count()
        self.stdout.write(f'Total jobs in database: {total_jobs}')