from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from tickets import views as tickets_views

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # User frontend urls
    url(r'^api/0.1/remain$', tickets_views.how_many_left),
    url(r'^book/(?P<show_id>\d+)/$', tickets_views.book_landing, name='book'),
    url(r'^book/(?P<show_id>\d+)/thanks/$', tickets_views.book_finish, name='finish'),
    url(r'^book/(?P<show_id>\d+)/error/$', tickets_views.book_error, name='error'),
    url(r'^cancel/(?P<ref_id>.*)/$', tickets_views.cancel, name='cancel'),
    url(r'^list/$', tickets_views.ListShows.as_view(), name='list'),
    url(r'^list-past/$', tickets_views.ListPastShows.as_view(), name='list-past'),
    url(r'^list/(?P<slug>[-_\w]+)/$', tickets_views.DetailShow.as_view(), name='detail'),
    url(r'^sidebar/$', tickets_views.sidebar, name='sidebar'),

    # Auth views
    # url(r'^login/$', tickets_views.LoginView, name='login'),
    url(r'^login/$', auth_views.login),
    url(r'^logout/$', auth_views.logout),

    # Admin urls
    url(r'^admin/', include(admin.site.urls)),

    # Admin frontend urls
    url(r'^$', tickets_views.ShowIndex, name='index'),
    url(r'^show/(?P<show_name>\d+)/$', tickets_views.ShowReport, name='show_report'),
    url(r'^show/(?P<show_name>\d+)/(?P<occ_id>\d+)/$', tickets_views.ShowReport, name='show_report_full'),

    # AJAX url handlers
    url(r'^show/(?P<show_name>\d+)/(?P<occ_id>\d+)/sale/$', tickets_views.SaleInputAJAX, name='sale_ajax'),
    url(r'^show/(?P<show_name>\d+)/(?P<occ_id>\d+)/reserve/$', tickets_views.ReserveInputAJAX, name='reserve_ajax'),

    # Sale report urls
    url(r'^report/$', tickets_views.SaleReport, name='sale_report'),
    url(r'^report/(?P<show_name>\d+)/$', tickets_views.SaleReportFull, name='sale_report_full'),

] 

if settings.DEBUG:
    urlpatterns = [
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),

] + urlpatterns
