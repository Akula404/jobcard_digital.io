import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# BASE DIRECTORY
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "boi3p)6(tiqfu42076ob!m+0b5&sqnvp=u@5%f(3x+&ws&z9r^"
)

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

CSRF_FAILURE_VIEW = "jobcard.csrf.csrf_failure"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "16.171.111.202",
    "ec2-16-171-111-202.eu-north-1.compute.amazonaws.com",
]


# -----------------------------
# APPLICATIONS
# -----------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'storages',
    "jobcard",
    "dashboard",
]


# -----------------------------
# MIDDLEWARE
# -----------------------------
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


# -----------------------------
# URLS / WSGI
# -----------------------------
ROOT_URLCONF = "project_simba.urls"

WSGI_APPLICATION = "project_simba.wsgi.application"


# -----------------------------
# TEMPLATES
# -----------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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


# -----------------------------
# DATABASE — AWS RDS MYSQL
# -----------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT", "3306"),

        "OPTIONS": {
            "charset": "utf8mb4",
        },

        "CONN_MAX_AGE": 600,
    }
}


# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]


# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = True


# -----------------------------
# STATIC FILES
# -----------------------------
STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# -----------------------------
# DEFAULT PRIMARY KEY
# -----------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -----------------------------
# LOGIN / LOGOUT
# -----------------------------
LOGIN_URL = "/jobcard/login/"

LOGIN_REDIRECT_URL = "/jobcard/redirect/"

LOGOUT_REDIRECT_URL = "/jobcard/login/"


# -----------------------------
# AWS S3 STORAGE
# -----------------------------

AWS_STORAGE_BUCKET_NAME = "digital-jobcard-signatures"
AWS_S3_REGION_NAME = "eu-north-1"

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# -----------------------------
# EMAIL — GMAIL SMTP
# -----------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.environ.get(
    "EMAIL_HOST",
    "smtp.gmail.com"
)

EMAIL_PORT = int(
    os.environ.get("EMAIL_PORT", "587")
)

EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER
)


# -----------------------------
# SESSION SETTINGS
# -----------------------------
# Leaving these disabled for now.
# Users can remain logged in during their production session
# and manually log out when finished.

# SESSION_COOKIE_AGE = 12 * 60 * 60
# SESSION_SAVE_EVERY_REQUEST = True