import datetime

from tastypie.resources import ModelResource

from models import *


class ShowResource(ModelResource):
    class Meta:
        today=datetime.date.today()
        queryset = Show.objects.filter(end_date__gte=today)
        resource_name = 'show'
