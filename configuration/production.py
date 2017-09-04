import os

ALLOWED_HOSTS = ['*']

import dj_database_url
DATABASES = {
        'default': dj_database_url.config()
        }

# STATIC_URL = "/static/"

# BASE_URL = 'ticketing.newtheatre.org.uk'

# AWS_STORAGE_BUCKET_NAME = "nt-tickets-static"
# STATICFILES_STORAGE = 'NT_Tickets.custom_storages.StaticStorage'
# STATICFILES_LOCATION = 'static'
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

# AWS_S3_SECURE_URLS = False    # Use HTTP instead of HTTPS
# AWS_QUERYSTRING_AUTH = False    # Remove auth querystrings from the query

# MEDIAFILES_LOCATION = 'media'
# MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
# DEFAULT_FILE_STORAGE = 'NT_Tickets.custom_storages.MediaStorage'

ACTUALLY_SEND_MAIL = True
