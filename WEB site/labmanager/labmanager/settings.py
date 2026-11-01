import os
from pathlib import Path
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = next(
    (folder / ".env" for folder in (BASE_DIR, *BASE_DIR.parents)
     if (folder / ".env").is_file()),
    None,
)
if ENV_FILE is not None:
    load_dotenv(ENV_FILE, override=False)

DJANGO_ENV = os.environ.get("DJANGO_ENV", "development").strip().lower()
if DJANGO_ENV not in {"development", "production"}:
    raise ImproperlyConfigured("DJANGO_ENV ha de ser development o production.")
PRODUCTION = DJANGO_ENV == "production"
DEBUG = not PRODUCTION

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY.strip():
    raise ImproperlyConfigured("Falta DJANGO_SECRET_KEY al .env del projecte o a l'entorn.")
if PRODUCTION and (
    len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5
    or SECRET_KEY.startswith("django-insecure-")
):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY no és adequada per a producció.")


def env_list(name, default=""):
    return list(dict.fromkeys(
        item.strip() for item in os.environ.get(name, default).split(",") if item.strip()
    ))


def env_bool(name, default="0"):
    value = os.environ.get(name, default).strip().lower()
    if value not in {"0", "1", "false", "true"}:
        raise ImproperlyConfigured(f"{name} ha de ser 0 o 1.")
    return value in {"1", "true"}


ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS", "" if PRODUCTION else "localhost,127.0.0.1,[::1]",
)
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Cal indicar DJANGO_ALLOWED_HOSTS.")
for host in ALLOWED_HOSTS:
    if (any(char in host for char in "/*?#@") or any(char.isspace() for char in host)
            or (":" in host and not (host.startswith("[") and host.endswith("]")))):
        raise ImproperlyConfigured(
            "DJANGO_ALLOWED_HOSTS ha de contenir hosts sense esquema, port ni '*'."
        )

CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
for origin in CSRF_TRUSTED_ORIGINS:
    try:
        parsed = urlsplit(origin)
        valid = (
            parsed.scheme in ({"https"} if PRODUCTION else {"http", "https"})
            and bool(parsed.hostname) and parsed.username is None and parsed.password is None
            and not parsed.path and not parsed.query and not parsed.fragment
            and "*" not in origin and not any(char.isspace() for char in origin)
        )
        parsed.port  #rebutja ports amb format incorrecte.
    except ValueError:
        valid = False
    if not valid:
        raise ImproperlyConfigured(
            "DJANGO_CSRF_TRUSTED_ORIGINS ha de contenir orígens complets sense ruta, "
            "a producció han d'usar HTTPS."
        )

SECURE_SSL_REDIRECT = PRODUCTION
SESSION_COOKIE_SECURE = PRODUCTION
CSRF_COOKIE_SECURE = PRODUCTION
JWT_COOKIE_SECURE = PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

#Activar només si un proxy de confiança fixa X-Forwarded-Proto i impedeix l'accés directe dels clients al servidor Django.
TRUST_PROXY_HTTPS = env_bool("DJANGO_TRUST_PROXY_HTTPS")
SECURE_PROXY_SSL_HEADER = (
    ("HTTP_X_FORWARDED_PROTO", "https") if PRODUCTION and TRUST_PROXY_HTTPS else None
)

#HSTS queda a 0 fins que el desplegament HTTPS s'hagi comprovat.
try:
    _hsts_seconds = int(os.environ.get("DJANGO_HSTS_SECONDS", "0"))
except ValueError as exc:
    raise ImproperlyConfigured("DJANGO_HSTS_SECONDS ha de ser un enter no negatiu.") from exc
if _hsts_seconds < 0:
    raise ImproperlyConfigured("DJANGO_HSTS_SECONDS ha de ser un enter no negatiu.")
SECURE_HSTS_SECONDS = _hsts_seconds if PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "core", "devices", "projects",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]
ROOT_URLCONF = "labmanager.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "labmanager.wsgi.application"

#BBDD interna de Django; les dades hidrològiques es consulten a través de l'API.
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3",
}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

#Django detecta core/static i devices/static perquè les apps estan instal·lades.
STATIC_URL = "/static/"
STATICFILES_DIRS = []
#Destinació de collectstatic. no és una carpeta d'origen.
STATIC_ROOT = BASE_DIR / "staticfiles"
