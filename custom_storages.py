from django.conf import settings
from storages.backends.s3boto import S3BotoStorage
import configuration.environment as env


if env.RUN_ENV == 'production':
  class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION

  class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION


elif env.RUN_ENV == 'development':
  class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION

elif env.RUN_ENV == 'staging':
  pass
