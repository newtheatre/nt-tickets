from django.conf import settings
from storages.backends.s3boto import S3BotoStorage
import os

DEBUG = bool(int(os.environ.get('DEBUG'))) if os.environ.get('DEBUG') else True
STAGING = bool(int(os.environ.get('STAGING'))) if os.environ.get('STAGING') else False

if not DEBUG and not STAGING:
  class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION

if not STAGING:
  class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION
