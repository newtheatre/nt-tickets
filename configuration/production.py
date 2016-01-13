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
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

ACTUALLY_SEND_MAIL = False
DO_CHIMP = False

MAX_DISCLOSURE = 80
