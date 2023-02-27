"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os, sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-u@9rqeiue_dk5!!k6l@6+yo%2yb^2rn@%8-3&#$7e&t9#w(8+@"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['project-a-15-f2022.herokuapp.com','127.0.0.1','127.0.0.1:8000','localhost']


# Application definition

INSTALLED_APPS = [
    #"django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bootstrap5",

    # created django apps
    'googleauth',

    # django-allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Google OAuth 2.0
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'templates', 'allauth')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
"""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
"""

"""
NOTE FOR WINSTON FROM WINSTON: RUN TESTS WITH -keepdb FLAG
"""

if 'test' in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": 'django.db.backends.postgresql_psycopg2',
            "NAME": 'd6ph1haqh5lm0b',
            "USER": 'uszjtqzaqrjvmg',
            "PASSWORD": '953b3bf0c16c211ba74d35cc9b409cde1a48767c5673e516396e64ee42278834',
            "HOST": 'ec2-44-208-236-253.compute-1.amazonaws.com',
            "PORT":  '5432',
            "TEST": {
                'NAME': 'd6ph1haqh5lm0b',        
                },
            },   
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": 'django.db.backends.postgresql_psycopg2',
            "NAME": 'dcg9mjo2u6gp5f',
            "USER": 'hporffixljsfiq',
            "PASSWORD": '30323f5c82c908b683c9c0e3c449954d5ca1c8f326b7e16a02ebc4648d34b3c3',
            "HOST": 'ec2-3-219-19-205.compute-1.amazonaws.com',
            "PORT":  '5432',
            "TEST": {
                'NAME': 'dcg9mjo2u6gp5f',        
                },
            },    
        }  
    
"""
Title: Provisioning a Test PostgreSQL database on Heroku for your Django App
URL: https://medium.com/analytics-vidhya/provisioning-a-test-postgresql-database-on-heroku-for-your-django-app-febb2b5d3b29

"""

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "EST"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static', 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Specify allauth backend, config settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

# Specify redirect URL on successful login
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

LOGIN_URL = '/'

# Other config settings for login
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True

# Enable email score to receive user email address after successful login
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

#Security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
# Change SECURE_SSL_REDIRECT to True when merging into main
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_HOST = 'project-a-15-f2022.herokuapp.com'
SECURE_HSTS_PRELOAD = True

"""
Author: Muhd Rahiman
Link: https://dev.to/mdrhmn/django-google-authentication-using-django-allauth-18f8 
Title: Django Google Authentication using django-allauth
"""