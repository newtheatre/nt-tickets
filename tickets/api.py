import datetime

from tastypie.resources import ModelResource

from models import *


class ShowResource(ModelResource):
    class Meta:
        today=datetime.date.today()
        queryset = Show.objects.filter(end_date__gte=today)
        resource_name = 'show'
        fields=['name','slug','location','description','poster','poster_wall',
        'poster_page','poster_tiny', 'start_date','end_date', 'category']
        allowed_methods = ['get']
