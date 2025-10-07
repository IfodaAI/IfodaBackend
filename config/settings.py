import os
import environ
from pathlib import Path
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Don't run with debug turned on in production!
SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("ALLOWED_HOSTS")
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

# Application definition

INSTALLED_APPS = [
    "daphne",
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
    "paytechuz.integrations.django",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "phonenumber_field",
    "django_filters",
    "channels",
    "corsheaders",
    "imagekit",
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
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware
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
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),  # Access token will last 3 days.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),  # Refresh token will last 14 days.
    "ROTATE_REFRESH_TOKENS": True,  # This makes simple_jwt return new refresh token if current one expired.
}

# Django Spectacular (Swagger generator) configurations.
SPECTACULAR_SETTINGS = {
    "TITLE": "Ifoda API",
    "DESCRIPTION": "Backend schema for Ifoda API.",
}

# Channels (WebSocket) configurations.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
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
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}

# Unfold Admin (Pretty admin panel) configurations.
UNFOLD = {
    "SITE_TITLE": "Ifoda Backend Admin Panel",  # This displays in login page as title.
    "SITE_HEADER": "Admin Panel",  # This is sidebar's title.
    "SITE_SUBHEADER": "Ifoda Backend Admin Panel.",  # This is sidebar's subtitle.
    "SITE_ICON": "/static/ifoda_favicon.png",  # This is sidebar's icon.
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": "/static/ifoda_favicon.png",
        },
    ],  # Admin panel's favicon.
    "THEME": "light",  # Force theme: "dark" or "light". Will disable theme switcher
    "LOGIN": {
        "image": "/static/ifoda_vertical.png"
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

# WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

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
STATIC_ROOT = os.path.join(BASE_DIR, "static_collected")
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

PAYTECHUZ = {
    "PAYME": {
        "PAYME_ID": "6881b7acd5ee42a97c8b6eff",
        "PAYME_KEY": "HJX&ESmd&ZJbZgGjuYii0uXMePcuuoHSVBN?",  #'WcXfTV&otM3XbTiNfzSYrj66RtvFrBK8oh%b',
        "ACCOUNT_MODEL": "orders.models.Order",  # For example: 'orders.models.Order'
        "ACCOUNT_FIELD": "order_id",
        "AMOUNT_FIELD": "amount",
        "IS_TEST_MODE": False,  # Ishlab chiqarishda False qiling
    },
    "CLICK": {
        "SERVICE_ID": "79480",
        "MERCHANT_ID": "30842",
        "MERCHANT_USER_ID": "48273",
        "SECRET_KEY": "KbcSKFP7TDVe",
        "ACCOUNT_MODEL": "orders.models.Order",  # For example: 'orders.models.Order'
        "ACCOUNT_FIELD": "order_id",
        "COMMISSION_PERCENT": 0.0,
        "IS_TEST_MODE": True,  # Ishlab chiqarishda False qiling
    },
}
