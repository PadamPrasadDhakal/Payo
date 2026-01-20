"""
Script to add sample organizations to the database.
Run this with: python manage.py shell < add_sample_organizations.py
Or: python manage.py runscript add_sample_organizations (if django-extensions installed)
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobsHaruPrj.settings')
django.setup()

from users.models import User
from django.contrib.auth.hashers import make_password

# Sample organizations data
sample_organizations = [
    {
        'username': 'techcorp',
        'email': 'contact@techcorp.com',
        'organization_name': 'TechCorp Solutions',
        'organization_website': 'https://techcorp.com',
        'organization_industry': 'Information Technology',
        'address': 'Kathmandu, Nepal',
        'phone': '9801234567',
        'bio': 'Leading IT solutions provider specializing in software development, cloud computing, and digital transformation. We help businesses leverage technology to achieve their goals.',
        'is_kyc_verified': True,
    },
    {
        'username': 'financeplus',
        'email': 'hr@financeplus.com',
        'organization_name': 'Finance Plus Ltd',
        'organization_website': 'https://financeplus.com',
        'organization_industry': 'Banking & Finance',
        'address': 'Lalitpur, Nepal',
        'phone': '9801234568',
        'bio': 'Premier financial services company offering banking, investment, and wealth management solutions. Building financial futures with innovation and trust.',
        'is_kyc_verified': True,
    },
    {
        'username': 'healthcarepro',
        'email': 'careers@healthcarepro.com',
        'organization_name': 'Healthcare Pro',
        'organization_website': 'https://healthcarepro.com',
        'organization_industry': 'Healthcare',
        'address': 'Pokhara, Nepal',
        'phone': '9801234569',
        'bio': 'Comprehensive healthcare solutions provider with state-of-the-art facilities and expert medical professionals dedicated to your well-being.',
        'is_kyc_verified': True,
    },
    {
        'username': 'edutech',
        'email': 'info@edutech.com',
        'organization_name': 'EduTech Institute',
        'organization_website': 'https://edutech.com',
        'organization_industry': 'Education',
        'address': 'Bhaktapur, Nepal',
        'phone': '9801234570',
        'bio': 'Pioneering educational technology company transforming learning experiences through innovative digital platforms and interactive content.',
        'is_kyc_verified': True,
    },
    {
        'username': 'constructionco',
        'email': 'jobs@constructionco.com',
        'organization_name': 'Construction Co Nepal',
        'organization_website': 'https://constructionco.com',
        'organization_industry': 'Construction',
        'address': 'Kathmandu, Nepal',
        'phone': '9801234571',
        'bio': 'Premier construction and infrastructure development company building modern Nepal with quality workmanship and sustainable practices.',
        'is_kyc_verified': True,
    },
    {
        'username': 'retailmart',
        'email': 'hr@retailmart.com',
        'organization_name': 'Retail Mart Nepal',
        'organization_website': 'https://retailmart.com',
        'organization_industry': 'Retail',
        'address': 'Kathmandu, Nepal',
        'phone': '9801234572',
        'bio': 'Largest retail chain in Nepal offering wide range of products with exceptional customer service and competitive prices.',
        'is_kyc_verified': False,
    },
    {
        'username': 'mediahouse',
        'email': 'careers@mediahouse.com',
        'organization_name': 'Media House Nepal',
        'organization_website': 'https://mediahouse.com',
        'organization_industry': 'Media & Entertainment',
        'address': 'Lalitpur, Nepal',
        'phone': '9801234573',
        'bio': 'Leading media and entertainment company producing quality content across TV, radio, and digital platforms.',
        'is_kyc_verified': True,
    },
    {
        'username': 'foodservice',
        'email': 'jobs@foodservice.com',
        'organization_name': 'Food Service Group',
        'organization_website': 'https://foodservice.com',
        'organization_industry': 'Food & Beverage',
        'address': 'Kathmandu, Nepal',
        'phone': '9801234574',
        'bio': 'Restaurant and catering services company delivering exceptional dining experiences with diverse cuisine options.',
        'is_kyc_verified': True,
    },
    {
        'username': 'travelagency',
        'email': 'info@travelagency.com',
        'organization_name': 'Travel Nepal Agency',
        'organization_website': 'https://travelagency.com',
        'organization_industry': 'Tourism & Travel',
        'address': 'Pokhara, Nepal',
        'phone': '9801234575',
        'bio': 'Expert travel agency offering customized tour packages, trekking expeditions, and adventure tourism across Nepal.',
        'is_kyc_verified': True,
    },
    {
        'username': 'manufacturingind',
        'email': 'hr@manufacturingind.com',
        'organization_name': 'Manufacturing Industries',
        'organization_website': 'https://manufacturingind.com',
        'organization_industry': 'Manufacturing',
        'address': 'Biratnagar, Nepal',
        'phone': '9801234576',
        'bio': 'Leading manufacturing company producing quality goods for both domestic and international markets.',
        'is_kyc_verified': False,
    },
    {
        'username': 'logisticsnet',
        'email': 'careers@logisticsnet.com',
        'organization_name': 'Logistics Network',
        'organization_website': 'https://logisticsnet.com',
        'organization_industry': 'Logistics & Transportation',
        'address': 'Kathmandu, Nepal',
        'phone': '9801234577',
        'bio': 'Comprehensive logistics and supply chain solutions provider ensuring efficient delivery across Nepal.',
        'is_kyc_verified': True,
    },
    {
        'username': 'energysolar',
        'email': 'info@energysolar.com',
        'organization_name': 'Energy Solar Solutions',
        'organization_website': 'https://energysolar.com',
        'organization_industry': 'Energy & Utilities',
        'address': 'Lalitpur, Nepal',
        'phone': '9801234578',
        'bio': 'Renewable energy company specializing in solar power solutions for residential and commercial applications.',
        'is_kyc_verified': True,
    },
    {
        'username': 'consultingpro',
        'email': 'jobs@consultingpro.com',
        'organization_name': 'Consulting Pro Nepal',
        'organization_website': 'https://consultingpro.com',
        'organization_industry': 'Consulting',
        'address': 'Kathmandu, Nepal',
        'phone': '9801234579',
        'bio': 'Professional consulting firm providing strategic business advice, management consulting, and process optimization.',
        'is_kyc_verified': True,
    },
    {
        'username': 'hotelresort',
        'email': 'hr@hotelresort.com',
        'organization_name': 'Hotel & Resort Nepal',
        'organization_website': 'https://hotelresort.com',
        'organization_industry': 'Hospitality',
        'address': 'Pokhara, Nepal',
        'phone': '9801234580',
        'bio': 'Luxury hotel and resort offering world-class accommodation and hospitality services in scenic locations.',
        'is_kyc_verified': True,
    },
    {
        'username': 'pharmalife',
        'email': 'careers@pharmalife.com',
        'organization_name': 'PharmaLife Nepal',
        'organization_website': 'https://pharmalife.com',
        'organization_industry': 'Pharmaceuticals',
        'address': 'Kathmandu, Nepal',
        'phone': '9801234581',
        'bio': 'Leading pharmaceutical company committed to improving healthcare through quality medicines and research.',
        'is_kyc_verified': False,
    },
]

def add_organizations():
    """Add sample organizations to the database"""
    created_count = 0
    skipped_count = 0
    
    print("=" * 60)
    print("ADDING SAMPLE ORGANIZATIONS")
    print("=" * 60)
    
    for org_data in sample_organizations:
        # Check if organization already exists
        if User.objects.filter(username=org_data['username']).exists():
            print(f"⏭️  Skipped: {org_data['organization_name']} (already exists)")
            skipped_count += 1
            continue
        
        # Create organization user
        try:
            org_user = User.objects.create(
                username=org_data['username'],
                email=org_data['email'],
                password=make_password('password123'),  # Default password
                user_type=User.UserType.ORGANIZATION,
                organization_name=org_data['organization_name'],
                organization_website=org_data['organization_website'],
                organization_industry=org_data['organization_industry'],
                address=org_data['address'],
                phone=org_data['phone'],
                bio=org_data['bio'],
                is_kyc_verified=org_data['is_kyc_verified'],
            )
            print(f"✅ Created: {org_data['organization_name']} ({org_data['organization_industry']})")
            created_count += 1
        except Exception as e:
            print(f"❌ Error creating {org_data['organization_name']}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: Created {created_count} | Skipped {skipped_count}")
    print("=" * 60)
    print("\n📝 Note: Default password for all organizations is 'password123'")
    print("🌐 Visit: http://127.0.0.1:8000/organization/directory/")
    print("=" * 60)

if __name__ == "__main__":
    add_organizations()
