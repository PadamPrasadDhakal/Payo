import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PayoPrj.settings')
django.setup()

from users.models import User

orgs = User.objects.filter(user_type='ORG')
print(f'\nTotal Organizations in Database: {orgs.count()}\n')
print('=' * 60)

for i, org in enumerate(orgs[:20], 1):
    industry = org.organization_industry or 'No Industry'
    name = org.organization_name or org.username
    verified = '✓' if org.is_kyc_verified else '✗'
    print(f'{i}. {name} ({industry}) - Verified: {verified}')

print('=' * 60)
