# Django settings for SeabirdGatewayPortal project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Martin Lukac', 'martin@nexleaf.org'),
    ('Lucas Howell', 'LJHowell@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'seabird',                      # Or path to database file if using sqlite3.
        'USER': 'seabird',                      # Not used with sqlite3.
        'PASSWORD': 'Z',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Path to project installation.
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/seabird/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/seabird/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9xjd^6wc@9d$=qzvsgxhukr'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'SeabirdGatewayPortal.urls'

LOGIN_URL = '/seabird/accounts/login/'
LOGOUT_URL = '/seabird/accounts/login/'
LOGIN_REDIRECT_URL = '/seabird/'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'SeabirdGatewayPortal',
)

TEMPLATE_CONTEXT_PROCESSORS =(
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'SeabirdGatewayPortal.common.context_processors.media_url'
)


#########################
# Data Portal Settings

DATA_WORK_DIR='/var/www/seabird/work/'
DATA_DOWNLOAD_DIR='/var/www/seabird/root/download/'
INCOMING_DIR='/var/www/seabird/incoming/'
# between zero and 9... check rsync settings too!
ZIP_COMPRESS=9

CRON_FILE="/var/www/seabird/conf/add_to_crontab.txt"
LOG_DIR="/var/www/seabird/log/"

# Determine if in production or dev, since DEBUG is always True
# Override it in settings_local for local dev.
DEV_ENVIRONMENT = False

# URLs to Main Server.
MAIN_SERVER_URL = 'http://seabird.nexleaf.org/seabird/'
BULK_CONFIGS_URL = os.path.join(MAIN_SERVER_URL, 'configuration/bulk/')

# Used to override these settings for local development.
try:
    from settings_local import *
except ImportError:
    pass
