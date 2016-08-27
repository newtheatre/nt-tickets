BASE_URL = "localhost:8000"
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'username'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True

ACTUALLY_SEND_MAIL = False
