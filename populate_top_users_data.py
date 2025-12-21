"""
Script to populate test data for the Top Users feature.
Run this with: python manage.py shell < populate_top_users_data.py
"""

from users.models import User
from django.db import transaction

# Sample data for users
users_data = [
    {
        'username': 'john_dev',
        'email': 'john@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'testpass123',
        'user_type': 'APP',
        'industry_field': 'technology',
        'experience_level': 'senior',
        'tagline': 'Senior Full Stack Developer | Python & React Expert',
        'bio': 'Experienced full-stack developer with 8+ years building scalable web applications. Passionate about clean code and mentoring junior developers.',
        'skills': 'Python, Django, React, PostgreSQL, AWS, Docker',
        'address': 'Kathmandu, Nepal',
        'education_qualification': 'Bachelor',
        'education_institute': 'Tribhuvan University',
        'shortlisted_count': 12,
        'selected_count': 8,
        'hired_count': 3,
    },
    {
        'username': 'sarah_designer',
        'email': 'sarah@example.com',
        'first_name': 'Sarah',
        'last_name': 'Johnson',
        'password': 'testpass123',
        'user_type': 'APP',
        'industry_field': 'technology',
        'experience_level': 'intermediate',
        'tagline': 'UX/UI Designer | Creating delightful user experiences',
        'bio': 'Creative designer focused on user-centered design. 5 years of experience in web and mobile app design.',
        'skills': 'Figma, Adobe XD, UI/UX Design, Prototyping, User Research',
        'address': 'Pokhara, Nepal',
        'education_qualification': 'Bachelor',
        'education_institute': 'Kathmandu University',
        'shortlisted_count': 10,
        'selected_count': 6,
        'hired_count': 2,
    },
    {
        'username': 'alex_analyst',
        'email': 'alex@example.com',
        'first_name': 'Alex',
        'last_name': 'Smith',
        'password': 'testpass123',
        'user_type': 'APP',
        'industry_field': 'finance',
        'experience_level': 'expert',
        'tagline': 'Financial Analyst | Data-Driven Investment Strategies',
        'bio': 'Expert financial analyst with 10+ years in investment banking and portfolio management.',
        'skills': 'Financial Modeling, Excel, Python, SQL, Risk Analysis, Bloomberg Terminal',
        'address': 'Lalitpur, Nepal',
        'education_qualification': 'Master',
        'education_institute': 'London School of Economics',
        'shortlisted_count': 15,
        'selected_count': 10,
        'hired_count': 4,
    },
    {
        'username': 'maria_teacher',
        'email': 'maria@example.com',
        'first_name': 'Maria',
        'last_name': 'Garcia',
        'password': 'testpass123',
        'user_type': 'APP',
        'industry_field': 'education',
        'experience_level': 'senior',
        'tagline': 'Education Specialist | STEM Curriculum Developer',
        'bio': 'Passionate educator with 8 years experience in curriculum development and teacher training.',
        'skills': 'Curriculum Development, STEM Education, Teacher Training, EdTech, Assessment Design',
        'address': 'Bhaktapur, Nepal',
        'education_qualification': 'Master',
        'education_institute': 'Tribhuvan University',
        'shortlisted_count': 9,
        'selected_count': 7,
        'hired_count': 2,
    },
    {
        'username': 'david_marketing',
        'email': 'david@example.com',
        'first_name': 'David',
        'last_name': 'Lee',
        'password': 'testpass123',
        'user_type': 'APP',
        'industry_field': 'marketing',
        'experience_level': 'intermediate',
        'tagline': 'Digital Marketing Specialist | SEO & Content Strategy',
        'bio': 'Results-driven marketer specializing in digital strategies and content marketing.',
        'skills': 'SEO, Google Ads, Content Marketing, Social Media, Analytics, Email Marketing',
        'address': 'Kathmandu, Nepal',
        'education_qualification': 'Bachelor',
        'education_institute': 'KUSOM',
        'shortlisted_count': 7,
        'selected_count': 5,
        'hired_count': 1,
    },
]

# Organization data
org_data = {
    'username': 'tech_org',
    'email': 'org@techcompany.com',
    'password': 'testpass123',
    'user_type': 'ORG',
    'organization_name': 'TechCo Nepal',
    'organization_industry': 'technology',
    'organization_website': 'https://techco.com.np',
    'address': 'Tinkune, Kathmandu',
}

print("Populating test data for Top Users feature...")

with transaction.atomic():
    # Create organization if it doesn't exist
    org, created = User.objects.get_or_create(
        username=org_data['username'],
        defaults=org_data
    )
    if created:
        org.set_password(org_data['password'])
        org.save()
        print(f"✓ Created organization: {org.username}")
    else:
        # Update industry if org exists but doesn't have one
        if not org.organization_industry:
            org.organization_industry = org_data['organization_industry']
            org.save()
        print(f"✓ Organization already exists: {org.username}")
    
    # Create test users
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            # Update profile score to calculate ranking and rating
            user.update_profile_score()
            print(f"✓ Created user: {user.username} (ranking: {user.employee_ranking}, rating: {user.profile_rating})")
        else:
            # Update existing user with new fields
            for key, value in user_data.items():
                if key not in ['username', 'password']:
                    setattr(user, key, value)
            user.save()
            user.update_profile_score()
            print(f"✓ Updated user: {user.username} (ranking: {user.employee_ranking}, rating: {user.profile_rating})")

print("\n✅ Data population complete!")
print(f"\nOrganization Login: username={org_data['username']}, password={org_data['password']}")
print(f"Organization Industry: {org_data['organization_industry']}")
print(f"\nCreated {len(users_data)} test users with various experience levels and skills.")
print(f"\nYou can now login as the organization and visit /organization/top-users/ to see the feature!")
