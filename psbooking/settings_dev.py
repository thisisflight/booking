from .settings_base import *

DEBUG = True

INSTALLED_APPS.append(
    'debug_toolbar'
)
MIDDLEWARE.insert(
    0, 'debug_toolbar.middleware.DebugToolbarMiddleware'
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
