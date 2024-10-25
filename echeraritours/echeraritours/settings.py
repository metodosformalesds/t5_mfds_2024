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
from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-avsk3*vt5klexdi1&z(l&a5wy2xhlxnu$9=1(s4%(do9tzko%_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#if 'PYTHONANYWHERE_DOMAIN' in os.environ:
#    ALLOWED_HOSTS = ['echeraritours.pythonanywhere.com']
#else:
#    ALLOWED_HOSTS = []
ALLOWED_HOSTS = []

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
            ],
        },
    },
]

WSGI_APPLICATION = 'echeraritours.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field


# AL RATO LE MOVEMOS A ESTO JIJI

# AUTHENTICATION_BACKENDS = (
#     'social_core.backends.google.GoogleOAuth2',
#     'social_core.backends.facebook.FacebookOAuth2',
#     'social_core.backends.apple.AppleIdAuth',
#     'django.contrib.auth.backends.ModelBackend',
# )

AUTHENTICATION_BACKENDS = (
    'apps.appUser.authentication_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'tu-google-client-id'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'tu-google-client-secret'

# SOCIAL_AUTH_FACEBOOK_KEY = 'tu-facebook-app-id'
# SOCIAL_AUTH_FACEBOOK_SECRET = 'tu-facebook-app-secret'

# SOCIAL_AUTH_APPLE_ID_CLIENT = 'tu-apple-client-id'
# SOCIAL_AUTH_APPLE_ID_TEAM = 'tu-apple-team-id'
# try:
#     SOCIAL_AUTH_APPLE_ID_KEY = open(BASE_DIR / 'tu_clave_privada.pem').read()
# except FileNotFoundError:
#     print("No se encontró el archivo tu_clave_privada.pem. Verifica la ruta.")
#     SOCIAL_AUTH_APPLE_ID_KEY = None  # O manejar el error de otra manera


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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
