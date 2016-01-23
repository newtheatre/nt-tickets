DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {    
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'NTTDB',
        'USER' : 'tickets',
        'PASSWORD' : 'Tickets01',
        'HOST' : 'nt-tickets-postgres-2.c9r4q51rnkwp.eu-west-1.rds.amazonaws.com',
        'PORT' : '5432',
    }
}

SITE_URL = 'newtheatre.org.uk'

AWS_STORAGE_BUCKET_NAME = "nt-tickets"
STATICFILES_STORAGE = 'custom_storages.StaticStorage'
STATICFILES_LOCATION = 'static'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

AWS_S3_SECURE_URLS = False    # Use HTTP instead of HTTPS
AWS_QUERYSTRING_AUTH = False    # Remove auth querystrings from the query

MEDIAFILES_LOCATION = 'media'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

ACTUALLY_SEND_MAIL = False
DO_CHIMP = False

MAX_DISCLOSURE = 10
