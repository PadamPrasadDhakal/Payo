from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-me-for-production",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

import os
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,192.168.18.134,*").split(",")

INSTALLED_APPS = [
    # Django default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd party apps
    "crispy_forms",
    "crispy_bootstrap4",
    "rest_framework",
    # "django_crontab",  # Uncomment after installing: pip install django-crontab
    
    # Authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Local apps
    "users",
    "jobs",
    "makecv",
    "organization",
    "api"
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # KYC enforcement middleware to block unverified orgs from posting
    "users.middleware.KycEnforcementMiddleware",
    # CMS redirect middleware to restrict staff users to admin/cms only
    "users.middleware.CMSRedirectMiddleware",
]

ROOT_URLCONF = "PayoPrj.urls"



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = "PayoPrj.wsgi.application"
ASGI_APPLICATION = "PayoPrj.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Crispy Forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Authentication settings
AUTH_USER_MODEL = "users.User"
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "users:dashboard"
LOGOUT_REDIRECT_URL = "home"


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
from dotenv import load_dotenv
load_dotenv()
SOCIALACCOUNT_PROVIDERS = {
  'google': {
    'APP': {
      'client_id': os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
      'secret': os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
      'key': ''
    }
  }
}

# Allauth settings
SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_AUTO_SIGNUP = True

# Email Configuration
# For development, use console backend (prints emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production, uncomment and configure SMTP settings:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # your email
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # your email password or app password

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@Payo.local')
CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'support@Payo.local')

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'unverified_apply': '2/day',  # Unverified users can apply to 2 jobs per day
    }
}

# Cron Jobs Configuration - Reset tokens daily at midnight
CRONJOBS = [
    ('0 0 * * *', 'django.core.management.call_command', ['reset_daily_tokens'], {'verbosity': 2}),
]