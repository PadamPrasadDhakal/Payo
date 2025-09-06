import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobsHaruPrj.settings')
django.setup()

from users.forms import ApplicantSignUpForm

form = ApplicantSignUpForm()
print("Form fields:")
for field_name in form.fields:
    print(f"- {field_name}: {form.fields[field_name].label}")