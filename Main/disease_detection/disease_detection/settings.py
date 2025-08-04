"""
Django settings for disease_detection project.
"""

import os
from pathlib import Path
from decouple import config

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# GitHub Codespaces configuration
CODESPACE_NAME = os.getenv('CODESPACE_NAME')

# Base allowed hosts
ALLOWED_HOSTS = ['*']

# Add Codespace-specific hosts if running in Codespaces
if CODESPACE_NAME:
    CODESPACE_HOSTS = [
        f'{CODESPACE_NAME}-8000.preview.app.github.dev',
        f'{CODESPACE_NAME}-8000.app.github.dev',
        '*.preview.app.github.dev',
        '*.app.github.dev',
    ]
    ALLOWED_HOSTS.extend(CODESPACE_HOSTS)
    
    # CSRF trusted origins for Codespaces
    CSRF_TRUSTED_ORIGINS = [
        f'https://{CODESPACE_NAME}-8000.preview.app.github.dev',
        f'https://{CODESPACE_NAME}-8000.app.github.dev',
    ]
    
    print(f"🚀 Codespace detected: {CODESPACE_NAME}")
    print(f"📱 Access your app at: https://{CODESPACE_NAME}-8000.preview.app.github.dev/")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'diagnosis',
    'users',
    'administrator',
    'vet',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'disease_detection.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Global templates directory
            BASE_DIR / 'users' / 'templates',  # Users app templates
        ],
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

WSGI_APPLICATION = 'disease_detection.wsgi.application'

# Database - Supabase PostgreSQL with Transaction Pooler
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('SUPABASE_DB_NAME'),
        'USER': config('SUPABASE_DB_USER'),
        'PASSWORD': config('SUPABASE_DB_PASSWORD'),
        'HOST': config('SUPABASE_DB_HOST'),
        'PORT': config('SUPABASE_DB_PORT', default='6543'),
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 30,
            'options': '-c default_transaction_isolation=read_committed'
        },
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': True,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'

# Static files directories - where Django looks for static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Your custom static files
]

# Disable STATIC_ROOT since we're not using collectstatic
# STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Force DEBUG to True for development server to serve static files
DEBUG = True

# Allow all hosts for deployment
ALLOWED_HOSTS = ['*']

# Static files finders (Django uses these to locate static files)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Login/Logout redirects
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Production Security Settings (only if not DEBUG)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Security settings for deployment
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Static files serving in production without nginx
WHITENOISE_USE_FINDERS = True