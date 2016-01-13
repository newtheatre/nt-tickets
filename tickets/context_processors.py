import configuration.customise
from django.conf import settings


def customise_processor(request):
    return {'customise': configuration.customise, }


def recaptcha(request):
  return {
    'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY,
  }
