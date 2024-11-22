"""
Django settings for pruebaDjangoPonce project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import environ
import logging
import paypalrestsdk
from dotenv import load_dotenv
# import pymysql


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-avsk3*vt5klexdi1&z(l&a5wy2xhlxnu$9=1(s4%(do9tzko%_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Aqui se utilizaria el dominio de pythonanywhere si se estuviera trabajando en pythonanywhere
# if 'PYTHONANYWHERE_DOMAIN' in os.environ:
#    ALLOWED_HOSTS = ['echeraritours.pythonanywhere.com']
# else:
# ALLOWED_HOSTS = ["echeraritours.live"]
# ALLOWED_HOSTS = ["35.95.38.255"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.appUser',
    'apps.appTour',
    'apps.appPayment',
    'apps.appDashboard',
    'widget_tweaks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'storages',
    # 'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'echeraritours.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.common.context_processors.registration_status',
            ],
        },
    },
]

WSGI_APPLICATION = 'echeraritours.wsgi.application'


# La base de datos debe ser cambiada segun sea el entorno de desarrollo o produccion
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'echeraritoursDB',  # Nombre de la base de datos en MySQL
#         'USER': 'Leonardo',  # Nombre de usuario de la base de datos
#         'PASSWORD': 'echeraritours',  # La contraseña que creaste
#         # El endpoint de la base de datos
#         'HOST': 'ls-d79a6da0aff3438baefae126ba22bb1cb9329666.cvya6wuiewji.us-west-2.rds.amazonaws.com',
#         'PORT': '3306',  # Puerto por defecto de MySQL
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Ajustado
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field


AUTHENTICATION_BACKENDS = (
    'apps.appUser.authentication_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': {
            'profile',
            'email'},
        'OAUTH_PARAMS': {'access_type': 'online'},
        'AUTH_PKCE_ENABLED': True,
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': True,
        'CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'SECRET': os.getenv('GOOGLE_SECRET'),
    }
}

ACCOUNT_AUTHENTICATION_METHOD = 'email'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
LOGIN_REDIRECT_URL = 'index'


# Esta seccion la modifique por mientras para que cualquiera
# pueda abrir el repo sin necesidad de tener que hacer el archivo .env
# load_dotenv()

# env = environ.Env()
# env_file = os.path.join(os.path.dirname(__file__), '.env')
# environ.Env.read_env(env_file)

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = env('EMAIL_HOST')
# EMAIL_PORT = env('EMAIL_PORT')
# EMAIL_USE_TLS = env('EMAIL_USE_TLS') == 'bool'
# EMAIL_HOST_USER = env('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Lo que hace aqui es que agarra valores predeterminados del repositorio personal
load_dotenv()

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.tu-servidor.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'correo@ejemplo.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'contraseña')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Llamadas a APIs desde el archivo .env
env = environ.Env()
environ.Env.read_env()
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY')

# Stripe jiji
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_MODE = os.getenv('PAYPAL_MODE')  # Puede ser "sandbox" o "live"


ID_ANALYZER_API_KEY = os.getenv('ID_ANALYZER_API_KEY')

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"


# DEFAULT_FILE_STORAGE = 'storages.backends_s3boto3.S3Boto3Storage'
