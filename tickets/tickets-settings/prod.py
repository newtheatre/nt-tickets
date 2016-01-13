# Server Django settings
from settings import *

DEBUG = False

TEMPLATE_DEBUG = False

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

AWS_STORAGE_BUCKET_NAME = "nt-tickets"
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL
