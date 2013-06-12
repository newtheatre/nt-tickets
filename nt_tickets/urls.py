from django.conf.urls import patterns, include, url

import tickets.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'tickets.views.defaultFNI', name='home'),
    url(r'^book/(?P<show_id>\d+)/$', 'tickets.views.book_landing', name='book'),
    url(r'^book/(?P<show_id>\d+)/thanks/$', 'tickets.views.book_finish'),
    url(r'^admin/report/$', 'tickets.views.report'),
    url(r'^list$', tickets.views.ListShows.as_view()),

    # url(r'^nt_tickets/', include('nt_tickets.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
