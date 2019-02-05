# endpoint                            method          result
#
# api/shows/                          get             list current shows for what's on
# api/shows/<id>                      get             get a specific show
# api/shows/filter/<category_slug>    get             filter shows to a specific category


from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db.models import Min
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context, RequestContext
import datetime

from tickets import models
from configuration import customise
from django.conf import settings


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'slug')


class OccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Occurrence
        fields = ('id', 'date', 'time', 'maximum_sell', 'tickets_sold', 'sold_out')


class ShowSerializer(serializers.HyperlinkedModelSerializer):
    occurrence_set = OccurrenceSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    # TODO get poster URL

    class Meta:
        model = models.Show
        fields = ('id', 'url', 'name', 'description', 'location', 'description', 'long_description', 'start_date', 'end_date', 'is_current', 'poster', 'category', 'occurrence_set', 'show_sold_out')


class ShowViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShowSerializer
    time_filter = datetime.date.today()
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
            return Response({"error": "Category not found"},
                            status=status.HTTP_404_NOT_FOUND)
