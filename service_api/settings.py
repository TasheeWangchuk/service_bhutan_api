
from pathlib import Path
import os
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files configuration
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CLOUDINARY_STORAGE = {
    'CLOUD_NAME':os.environ.get('CLOUDINARY_CLOUD_NAME','dcaqk4wut') ,
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY','721239442467743'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET','Rb2d_akyiO3M8OXzJ4Bwb5jQeCE')
}

# Set Cloudinary as your default file storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# LocalHost
# SECRET_KEY = 'django-insecure-@8*)2cpm!w=z$0pi$#+9*&!@1i82-orc=g#(q3*)0iy&rkmuqa'
# DEBUG = True
# ALLOWED_HOSTS = []

# render
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'user',
    'job',
    'rest_framework.authtoken',
    'notification',
    'portfolio',
    'contract',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
    'cloudinary',
    'cloudinary_storage'
]

# CORS headers
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", 
    "http://localhost:3001"
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Since you're using JWT, add these settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Templates
ROOT_URLCONF = 'service_api.urls'
TEMPLATES_ROOT = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_ROOT],
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

WSGI_APPLICATION = 'service_api.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_DRIVER','django.db.backends.postgresql_psycopg2'),
        'USER': os.environ.get('PG_USER','postgres'),
        'PASSWORD':os.environ.get('PG_PASSWORD','123'),
        'NAME': os.environ.get('PG_DB','service_api_db'),
        'PORT': os.environ.get('PG_PORT','5432'),
        'HOST': os.environ.get('PG_HOST','localhost'), # uses the container if set, otherwise it runs locally
    }
}

# """Render database_url variable"""
database_url = os.environ.get('DATABASE_URL')

# """External Database Connection"""
# database_url ="postgresql://service_bhutan_database_u452_user:EMW9XFgDmJtzNBSihyn4LULhWqpMJT1k@dpg-cukettt6l47c73cas0i0-a.oregon-postgres.render.com/service_bhutan_database_u452"

DATABASES["default"] = dj_database_url.parse(database_url)

AUTH_USER_MODEL = "user.CustomUser"

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

USE_TZ = True


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}
    
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'USER_ID_FIELD': 'user_id',  
    'USER_ID_CLAIM': 'user_id',  
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  
]


CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST','smtp.gmail.com')
EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER','tashiwangchuk619@gmail.com')
EMAIL_HOST_USER_PASSWORD = os.getenv('EMAIL_HOST_USER_PASSWORD','nmhd phid hbon uxnq')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL','tashiwangchuk619@gmail.com')
HOST_URL='https://service-bhutan-api-o2oc.onrender.com'




