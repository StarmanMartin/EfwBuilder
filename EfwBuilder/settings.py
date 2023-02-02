"""
Django settings for EfwBuilder project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-mb2dlfw1jc#&fpi@=(-0ls$%_+l1o+f+ks$y9wuwl7q1qj+h_b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =  os.environ.get('FLAVOR') != 'production'



if not DEBUG:
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOST').split(',')
    PORT = os.environ.get('PORT') or ""
    PORT = PORT.strip(':')
    if PORT == "80":
        PORT = ""
    else:
        PORT = ":%s" % PORT
    CSRF_TRUSTED_ORIGINS = ['http://%s%s' % (x, PORT) for x in os.environ.get('ALLOWED_HOST').split(',')] + ['https://%s%s' % (x, PORT) for x in os.environ.get('ALLOWED_HOST').split(',')]
    WEBDAV_HOST = "%s%s" % (os.environ.get('WEBDAV_HOST'), PORT)
else:
    WEBDAV_HOST = "http://127.0.0.1:8000"
    ALLOWED_HOSTS = ['*']

# Application definition

VERSION=0.2

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'sdc_tools',
    'sdc_user',
    'Utils',
    'Adminview',
    'Dashboard',
    'Logedout',

]

INTERNAL_IPS = (
    '127.0.0.1',
    '0.0.0.0',
)

if DEBUG:
    INSTALLED_APPS += ['sdc_manager']


AUTH_USER_MODEL = 'sdc_user.CustomUser'
AUTHENTICATION_BACKENDS = ['sdc_user.backend.EmailBackend']



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'EfwBuilder.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

# WSGI_APPLICATION = 'EfwBuilder.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'elnFiletransfer.db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_NAME'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': 'db',
            'PORT': 5432,
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

#DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

STATIC_ROOT =  BASE_DIR /  'www/'

STATICFILES_DIRS = [ BASE_DIR /  "static",  BASE_DIR / 'node_modules']

ASGI_APPLICATION = 'EfwBuilder.asgi.application'

if DEBUG:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [('redis', 6379)],
            },
        },
    }

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

#EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST =''
#EMAIL_PORT = 587
#EMAIL_HOST_USER = ''
#DEFAULT_FROM_EMAIL = ''
#EMAIL_HOST_PASSWORD = ''
#EMAIL_USE_TLS = True

GOOS =  "windows"
GOROOT = os.environ.get('GOROOT')
GOPATH = os.environ.get('GOPATH')

if DEBUG:
    ELN_DEVICE_NAME="EFTM"
    ELN_URL="http://127.0.0.1:3000"
    MAX_UPLOAD_SIZE=os.environ.get('MAX_UPLOAD_SIZE', 250000)

else:
    ELN_DEVICE_NAME = os.environ.get('ELN_DEVICE_NAME', 'EFTM')
    ELN_URL=os.environ.get('ELN_URL')
    MAX_UPLOAD_SIZE=os.environ.get('MAX_UPLOAD_SIZE', 5e+7)

