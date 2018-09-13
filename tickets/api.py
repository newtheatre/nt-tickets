'''
endpoint                method          result

api/shows/list          get             list current shows for whatson
api/shows/<id>          get             get a specific show

api/tickets/book/<id>   post            book a ticket

'''

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404
from django.db.models import Min
import datetime

from tickets import models


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

    class Meta:
        model = models.Show
        fields = ('id', 'url', 'name', 'start_date', 'end_date', 'is_current', 'category', 'occurrence_set')


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
