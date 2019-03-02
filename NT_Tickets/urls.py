"""
NT_Tickets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from rest_framework import routers

from tickets import views, api

from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'shows', api.ShowViewSet)
# router.register(r'book', api.BookingViewSet, base_name='book')

urlpatterns = [
    # User frontend urls
    url(r'^api/0.1/remain$', views.how_many_left),
    url(r'^book/(?P<show_id>\d+)/$', views.book_landing, name='book'),
    url(r'^book/(?P<show_id>\d+)/thanks/$', views.book_finish, name='finish'),
    url(r'^book/(?P<show_id>\d+)/error/$', views.book_error, name='error'),
    url(r'^cancel/(?P<ref_id>.*)/$', views.cancel, name='cancel'),
    url(r'^list/$', views.ListShows.as_view(), name='list'),
    url(r'^list-past/$', views.ListPastShows.as_view(), name='list-past'),
    url(r'^list/(?P<slug>[-_\w]+)/$', views.DetailShow.as_view(), name='detail'),
    url(r'^sidebar/$', views.sidebar, name='sidebar'),

    url(r'^list-stuff-theatre/$', views.ListStuFFShows.as_view(), name='stuff-list'),

    # Auth views
    # url(r'^login/$', tickets_views.LoginView, name='login'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),

    # Admin urls
    url(r'^admin/', include(admin.site.urls)),

    # Admin frontend urls
    url(r'^$', login_required(views.ShowIndex.as_view()), name='index'),
    url(r'^show/(?P<show_name>\d+)/$', views.ShowReport, name='show_report'),
    url(r'^show/(?P<show_name>\d+)/(?P<occ_id>\d+)/$',
        views.ShowReport, name='show_report_full'),
    url(r'download/(?P<show_name>\d+)/$', views.DownloadReport, name='download_report'),
    url(r'^graph/$', views.graph_view, name='graph_view'),

    # AJAX url handlers
    url(r'^show/(?P<show_name>\d+)/(?P<occ_id>\d+)/sale/$',
        login_required(views.SaleInputAJAX), name='sale_ajax'),
    url(r'^show/(?P<show_name>\d+)/(?P<occ_id>\d+)/reserve/$',
        views.ReserveInputAJAX, name='reserve_ajax'),
    url(r'bug/$', views.GenReportAJAX, name='bug_ajax'),

    # Sale report urls
    url(r'^report/$', login_required(views.SaleReport.as_view()), name='sale_report'),
    url(r'^report/all/$', login_required(views.SaleReportAll.as_view()), name='sale_report_all'),
    url(r'^report/(?P<show_name>\d+)/$', views.SaleReportFull, name='sale_report_full'),

    # API Urls
    url(r'^api/', include(router.urls)),
]
