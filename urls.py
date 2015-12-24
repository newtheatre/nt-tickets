from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

from tickets import views as tickets_views

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^api/0.1/remain$', tickets_views.how_many_left),
    url(r'^book/(?P<show_id>\d+)/$', tickets_views.book_landing, name='book'),
    url(r'^book/(?P<show_id>\d+)/thanks/$', tickets_views.book_finish, name='finish'),
    url(r'^book/(?P<show_id>\d+)/error/$', tickets_views.book_error, name='error'),
    url(r'^cancel/(?P<ref_id>.*)/$', tickets_views.cancel, name='cancel'),
    url(r'^list/$', tickets_views.ListShows.as_view(), name='list'),
    url(r'^list-past/$', tickets_views.ListPastShows.as_view(), name='list-past'),
    url(r'^list/(?P<slug>[-_\w]+)/$', tickets_views.DetailShow.as_view(), name='detail'),
    url(r'^sidebar/$', tickets_views.sidebar, name='sidebar'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', login_required(tickets_views.ShowIndex), name='index'),
    url(r'^(?P<show_name>[0-9]{1})/$', tickets_views.ShowReport, name='show_report'),
    url(r'^(?P<show_name>[0-9]{1})/(?P<occ_id>[0-9]{1})/$', tickets_views.ShowReport, name='show_report_full'),
] 

if settings.DEBUG:
    urlpatterns = [
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
] + urlpatterns