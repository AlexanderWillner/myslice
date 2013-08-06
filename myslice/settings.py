# -*- coding: utf-8 -*-
# Django settings for myslice project.

import os
gettext = lambda s: s
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

import os.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# compute ROOT from where this file is installed
# should fit every need including developers
# but you can redefine ROOT if that's not working for you
try:
    # get the directory where this file is
    ROOT=os.path.dirname(__file__) or '.'
    # move one step up
    ROOT=os.path.realpath(ROOT+'/..')
except:
    ROOT=None
    if DEBUG:
        import traceback
        traceback.print_exc()

if not ROOT:
    raise Exception,"Cannot find ROOT for myslice"

####################
ADMINS = (
    # ('your_name', 'your_email@test.com'),
)

MANAGERS = ADMINS

# Mail configuration
#DEFAULT_FROM_EMAIL = "root@theseus.ipv6.lip6.fr"
#EMAIL_HOST_PASSWORD = "mypassword"

EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_USE_TLS = False





DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(ROOT,'myslice.sqlite3'), # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ROOT,'django-static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/all-static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT,'all-static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 't%n(3h)&amp;r^n8(+8)(sp29t^$c2#t(m3)e2!02l8w1#36tl#t27'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # CMS
    'cms.middleware.multilingual.MultilingualURLMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
)

# CMS
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
)


ROOT_URLCONF = 'myslice.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'myslice.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT,"all-templates"),

    # CMS
    os.path.join(PROJECT_PATH, "templates"),
)

# CMS
CMS_TEMPLATES = (
    ('template_1.html', 'Template One'),
    ('template_2.html', 'Template Two'),
)
LANGUAGES = [
    ('en', 'English'),
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # handling the {% insert %} and {% container %} tags
    # see details in devel/django-insert-above-1.0-4
    'insert_above',
    # our django project
    'myslice',
    # the core of the UI
    'auth', 'manifold', 'unfold',
    # plugins
    'plugins',
    # views - more or less stable 
    'views',
    'trash',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'portal',
# DEPRECATED #    'django.contrib.formtools',
# DEPRECATED ##    'crispy_forms',
# DEPRECATED #
# DEPRECATED #    # User registration
# DEPRECATED #    'django.contrib.auth',
# DEPRECATED #    'django.contrib.sites',
# DEPRECATED #    'registration',

    # CMS : Django CMS
    'cms',     # django CMS itself
    'mptt',    # utilities for implementing a modified pre-order traversal tree
    'menus',   # helper for model independent hierarchical website navigation
    'south',   # intelligent schema and data migrations
    'sekizai', # for javascript and css management
    # + plugins:
    'cms.plugins.flash',
    'cms.plugins.googlemap'
    'cms.plugins.link',
    'cms.plugins.snippet',
    'cms.plugins.text',
    'cms.plugins.twitter',
    # either
    'cms.plugins.file',
    'cms.plugins.picture',
    'cms.plugins.teaser',
    'cms.plugins.video',
    # or
    #'filer',
    #'cmsplugin_filer_file',
    #'cmsplugin_filer_folder',
    #'cmsplugin_filer_image',
    #'cmsplugin_filer_teaser',
    #'cmsplugin_filer_video',

    # Versioning of content 
    'reversion',
)

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTHENTICATION_BACKENDS = ( 'auth.backend.MyCustomBackend', 'auth.manifoldbackend.ManifoldBackend', )

### the view to redirect malformed (i.e. with a wrong CSRF) incoming requests
# without this setting django will return a 403 forbidden error, which is fine
# if you need to see the error message then use this setting
CSRF_FAILURE_VIEW = 'manifold.manifoldproxy.csrf_failure'

#################### for insert_above
#IA_JS_FORMAT = "<script type='text/javascript' src='{URL}' />"
# put stuff under static/
# IA_MEDIA_PREFIX = '/code/'

