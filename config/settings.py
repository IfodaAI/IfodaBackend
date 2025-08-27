import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG")

ALLOWED_HOSTS = os.environ.get("ALLOWED_DOMAINS").split(",")
CORS_ALLOWED_ORIGINS = os.environ.get("ALLOWED_DOMAINS").split(",")

# Application definition

INSTALLED_APPS = [
    # App for prettier django admin panel. MUST BE ON TOP OF ALL APPS.
    "unfold",
    # Django's default apps.
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "phonenumber_field",
    "django_filters",
    "corsheaders",
    # Local apps
    "users",
    "products",
    "chats",
    "orders",
    "payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
AUTH_USER_MODEL = "users.User"
PHONENUMBER_DEFAULT_REGION = "UZ"  # This configuration is required since backend must only accept phone numbers of Uzbekistan.
PHONENUMBER_DB_FORMAT = "E164"  # Forces phone number inputs such as "998901234567", "+998 90 123 45 67", "00998901234567" to be stored in database as +998901234567.

# Simple JWT (Authorization) configurations.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),  # Access token will last 3 days.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),  # Refresh token will last 14 days.
    "ROTATE_REFRESH_TOKENS": True,  # This makes simple_jwt return new refresh token if current one expired.
}

# Django Spectacular (Swagger generator) configurations.
SPECTACULAR_SETTINGS = {
    "TITLE": "Ifoda API",
    "DESCRIPTION": "Backend schema for Ifoda API.",
}

# Django Rest Framework (API) configurations.
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# Unfold Admin (Pretty admin panel) configurations.
UNFOLD = {
    "SITE_TITLE": "Ifoda Backend Admin Panel",  # This displays in login page as title.
    "SITE_HEADER": "Admin Panel",  # This is sidebar's title.
    "SITE_SUBHEADER": "Ifoda Backend Admin Panel.",  # This is sidebar's subtitle.
    "SITE_ICON": "https://i.postimg.cc/yDPjYkzB/ifoda-favicon.png",  # This is sidebar's icon.
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": "https://i.postimg.cc/yDPjYkzB/ifoda-favicon.png",
        },
    ],  # Admin panel's favicon.
    "THEME": "light",  # Force theme: "dark" or "light". Will disable theme switcher
    "LOGIN": {
        "image": "https://i.postimg.cc/xXYg2Lht/ifoda-vertical.jpg"
    },  # This displays in login page as banner
    "BORDER_RADIUS": "8px",  # Border corner radius for all admin panel components.
    "COLORS": {
        "primary": {
            "50": "247, 248, 247",
            "100": "230, 250, 218",
            "200": "201, 246, 182",
            "300": "158, 230, 140",
            "400": "117, 205, 104",
            "500": "107, 192, 104",
            "600": "64, 172, 60",
            "700": "30, 123, 42",
            "800": "19, 99, 36",
            "900": "11, 82, 33",
            "950": "12, 19, 12",
        },
    },  # Green color on all levels.
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "command_search": True,  # Replace the sidebar search with the command search
    },
}


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
