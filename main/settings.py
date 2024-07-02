import os
from pathlib import Path
from datetime import timedelta
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-7#tf3ucg0gq$l)-vie^69whd_r2y0(d8el9md25-h8)e@zkpo7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# VARIABLES DE REDIRECT
LOGIN_REDIRECT_URL = '/project/list/'
LOGOUT_REDIRECT_URL = '/'


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'axes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'apps.apps.AppsConfig',

    # Apps Login
    "apps.Login.apps.LoginConfig",

    # Apps Project
    "apps.Project.apps.ProjectConfig"


    #
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django_auto_logout.middleware.auto_logout',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'main.urls'

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

                'django_auto_logout.context_processors.auto_logout_client',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'BibCleanMerge',
        'HOST': 'DESKTOP-PLOD91E',
        'PORT': '',

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'trusted_connection': 'yes',
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# RUTA PARA LOS ARCHIVOS PROCESADOS RAPIDAMENTE
MEDIA_BIB = os.path.join(MEDIA_ROOT, 'files', 'bib')

# Si no existe el path de bib, lo crea
os.makedirs(MEDIA_BIB, exist_ok=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


PHOTO_USER_EMPTY = 'img/perfil/default.jpg'

# Tamaño máximo para archivos subidos en bytes (por defecto 2.5MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB


AUTH_USER_MODEL = 'Login.User'

# Configuraciones para conexión con un correo
EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'bcarrielr@unemi.edu.ec'
EMAIL_HOST_PASSWORD = 'brignercr10'
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'


# confirguracion para el admin mediante jazmin
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "BibCleanMerge",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "profile-picture",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "BibCleanMerge Admin",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "img/logo/logo.png",

    # Welcome text on the login screen
    "welcome_sign": "Bienvenido al Administrador de ",

    # Copyright on the footer
    "copyright": "Acme Library Ltd",


    "custom_css": "css/custom_admin.css",

}
# Esto es para controlar el tiempo de inactividad y posterior cerrado ce sesión
AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=1),
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
    'MESSAGE': 'La sesión ha expirado. Vuelva a iniciar sesión para continuar.',
}

#Controlar la cantidad de intentos de inicio de sesión, en este caso se limitó a 5 intentos(NO FUNCIONA)

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=5)
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']