import os
from pathlib import Path
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== SECURITY & ENVIRONMENT ====================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default=os.environ.get('SECRET_KEY', 'company-prod-secure-key-2024-mgsa-5000-users'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Company deployment hosts - Using your Render domain
ALLOWED_HOSTS = [
    #'mgsa-student-portal.onrender.com',
    'zestful-optimism-mgsa-student-portal.up.railway.app',
    'localhost',
    '127.0.0.1',
]

# ==================== APPLICATION DEFINITION ====================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps (Company approved)
    'rest_framework',
    'corsheaders',
    # 'django_filters',  # REMOVED - causing errors
    'cloudinary',
    'cloudinary_storage',
    'knox',
    'whitenoise',

    # Company business apps
    'accounts',
    'posts',
    'resources',
    'tutorials',
    'analytics',
    'executive',    
    'students',    
]

MIDDLEWARE = [
    # Security and CORS
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # Django core
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mgsa_backend.urls'

# ==================== TEMPLATES ====================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'mgsa_backend.wsgi.application'

# ==================== DATABASE CONFIGURATION ====================

# SQLite Database - Optimized for 5000 users
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'company_database.sqlite3',
        'OPTIONS': {
            'timeout': 30,  # Increased timeout for better concurrency
        }
    }
}


# ==================== SECURITY CONFIGURATION ====================

# Password validation for company security standards
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Company security policy
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'

# CSRF trusted origins for your Render domain
CSRF_TRUSTED_ORIGINS = [
    #'https://mgsa-student-portal.onrender.com',
    "https://zestful-optimism-mgsa-student-portal.up.railway.app",
]

# ==================== API & REST FRAMEWORK ====================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'knox.auth.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        # 'django_filters.rest_framework.DjangoFilterBackend',  # REMOVED
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
}

# Remove browsable API in production
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',
    ]

# ==================== KNOX TOKEN CONFIGURATION ====================

REST_KNOX = {
    'TOKEN_TTL': timedelta(days=30),
    'TOKEN_LIMIT_PER_USER': 3,
    'AUTO_REFRESH': False,
    'USER_SERIALIZER': 'accounts.serializers.UserSerializer',
}

# ==================== CORS CONFIGURATION ====================

# CORS settings for your Render domain
CORS_ALLOWED_ORIGINS = [
    "https://mgsa-student-portal.onrender.com",
]

# Development origins
if DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])

CORS_ALLOW_CREDENTIALS = True

# ==================== STATIC FILES CONFIGURATION ====================

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==================== INTERNATIONALIZATION ====================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==================== COMPANY SPECIFIC SETTINGS ====================

# Company information
COMPANY_NAME = "MGSA Student Portal"
COMPANY_EMAIL = "admin@mgsa-company.com"
COMPANY_SUPPORT_EMAIL = "support@mgsa-company.com"
MAX_USERS = 5000

# ==================== CUSTOM USER MODEL ====================

AUTH_USER_MODEL = 'accounts.User'

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/student-dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True

# ==================== EMAIL CONFIGURATION ====================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# ==================== CLOUDINARY CONFIGURATION ====================

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ==================== RENDER SPECIFIC SETTINGS ====================

# Detect if running on Render
if 'RENDER' in os.environ:
    # Ensure static files are collected
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # Security settings for Render
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'