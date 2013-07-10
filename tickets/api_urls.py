from django.conf.urls import patterns, include, url
from tastypie.api import Api
from api import ShowResource

tickets = Api(api_name='tickets')
tickets.register(ShowResource())

urlpatterns = patterns('', 
	url(r'',include(tickets.urls)),
)
