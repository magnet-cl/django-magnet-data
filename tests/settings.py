import os

DEBUG = True
SECRET_KEY = os.environ.get("MAGNETDATA_TEST_DJANGO_SECRET_KEY", "magnetdata")
SITE_ID = 1
TIME_ZONE = "UTC"
USE_TZ = True
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        # use a on-disk db for test so --reuse-db can be used
        "TEST": {"NAME": os.path.join(BASE_DIR, "test_db.sqlite3")},
    }
}

INSTALLED_APPS = [
    "magnet_data.apps.MagnetDataConfig",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
