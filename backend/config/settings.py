import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY') or 'default-insecure-key-for-development-learnpath-ai'

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,*').split(',') if host.strip()]

INSTALLED_APPS = [
    'daphne',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'channels',
    'core',
    'database',
    'authentication',
    'users',
    'profiles',
    'goals',
    'skills',
    'onboarding',
    'learning_history',
    'resources',
    'courses',
    'projects',
    'assessments',
    'learning_paths',
    'recommendations',
    'progress',
    'feedback',
    'notifications',
    'chat',
    'external_resources',
    'analytics',
    'moderation',
    'audit',
    'admin_portal',
    'platform_settings',
    'ai_integrations',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer' if os.getenv('USE_INMEMORY_CHANNEL', 'False').lower() not in ('true', '1') else 'channels.layers.InMemoryChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'learnpath_ai')

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or 'jwt-insecure-secret-learnpath-2026'
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '60'))
JWT_REFRESH_TOKEN_LIFETIME_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))

ADMIN_INITIAL_EMAIL = os.getenv('ADMIN_INITIAL_EMAIL', 'admin@learnpath.ai')
ADMIN_INITIAL_PASSWORD = os.getenv('ADMIN_INITIAL_PASSWORD', 'AdminSecurePass123!')
ADMIN_INITIAL_NAME = os.getenv('ADMIN_INITIAL_NAME', 'System Administrator')

AI_SERVICE_BASE_URL = os.getenv('AI_SERVICE_BASE_URL', 'http://localhost:8001/v1')
AI_SERVICE_API_KEY = os.getenv('AI_SERVICE_API_KEY', 'ai-service-internal-key')
AI_SERVICE_TIMEOUT = int(os.getenv('AI_SERVICE_TIMEOUT', '30'))

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN', '')
KAGGLE_API_KEY = os.getenv('KAGGLE_API_KEY', '')

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173').split(',') if origin.strip()]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'UNAUTHENTICATED_USER': None,
}
