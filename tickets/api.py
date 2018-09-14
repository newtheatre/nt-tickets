
# endpoint                            method          result
#
# api/shows/                          get             list current shows for what's on
# api/shows/<id>                      get             get a specific show
# api/shows/filter/<category_slug>    get             filter shows to a specific category
# api/shows/sidebar                   get             get the shows for the sidebar
#
# api/tickets/book/<id>               post            book a ticket


from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404
from django.db.models import Min
import datetime

from tickets import models
from configuration import customise


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('name', 'slug')


class OccurrenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Occurrence
        fields = ('date', 'time', 'maximum_sell', 'tickets_sold', 'sold_out')


class ShowSerializer(serializers.HyperlinkedModelSerializer):
    occurrence_set = OccurrenceSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    # TODO get poster URL

    class Meta:
        model = models.Show
        fields = ('id', 'url', 'name', 'start_date', 'end_date', 'is_current', 'poster', 'category', 'occurrence_set')


class ShowViewSet(viewsets.ModelViewSet):
    serializer_class = ShowSerializer
    time_filter = datetime.date.today() - datetime.timedelta(days=1)
    queryset = models.Show.objects.filter(end_date__gte=time_filter) \
        .annotate(earliest_occurrence_time=Min('occurrence__time'), earliest_occurrence_date=Min('occurrence__date')) \
        .order_by('start_date', 'earliest_occurrence_date', 'earliest_occurrence_time')

    @action(detail=False, url_name='category-filter', url_path='filter/(?P<category>.+)')
    def category_filter(self, request, category=None):
        if category is not None:
            queryset = self.queryset.filter(category__slug=category)
            queryset = self.paginate_queryset(queryset)

            serializer = self.get_serializer(queryset, context={'request': request}, read_only=True, many=True)

            return self.get_paginated_response(serializer.data)
        else:
            return Http404

    @action(detail=False, url_name='list-past-shows', url_path='past')
    def list_past_shows(self, request):
        today = datetime.date.today()

        queryset = models.Show.objects.filter(end_date__lte=today).order_by('-start_date')
        queryset = self.paginate_queryset(queryset)

        serializer = self.get_serializer(queryset, context={'request': request}, read_only=True, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_name='sidebar', url_path='sidebar')
    def sidebar(self, request):
        today = datetime.date.today()
        limit = today + datetime.timedelta(weeks=customise.SIDEBAR_FILTER_PERIOD)

        current_shows = list()
        for category in customise.PUBLIC_CATEGORIES:
            show = models.Show.objects \
                .filter(category__slug=category) \
                .filter(end_date__gte=today) \
                .order_by('end_date') \
                .filter(start_date__lte=limit)[:1]

            current_shows.append(
                self.get_serializer(show, context={'request': request}, read_only=True, many=True).data
            )

        return Response(current_shows)
