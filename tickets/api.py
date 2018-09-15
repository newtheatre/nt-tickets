# endpoint                            method          result
#
# api/shows/                          get             list current shows for what's on
# api/shows/<id>                      get             get a specific show
# api/shows/filter/<category_slug>    get             filter shows to a specific category
# api/shows/sidebar                   get             get the shows for the sidebar
#
# api/book/                           post            book a ticket
#   occurrence_id
#   person_name
#   email_address
#   quantity
#
# api/book/cancel                     post            cancel a ticket
#   ticket_id


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
        fields = ('id', 'url', 'name', 'start_date', 'end_date', 'is_current', 'poster', 'category', 'occurrence_set')


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = ('id', 'unique_code', 'stamp', 'person_name', 'email_address', 'quantity', 'cancelled', 'collected')


class ShowViewSet(viewsets.ModelViewSet):
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


class BookingViewSet(viewsets.ViewSet):
    serializer_class = TicketSerializer
    queryset = models.Ticket.objects.all()

    def list(self):
        queryset = models.Ticket.objects.all().order_by('-stamp')
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def send_mail(**kwargs):
        reservation = kwargs.pop('reservation')
        # Send a confirmation email, probs move this so cancel can use this too
        email_html = get_template('email/confirm_inline.html').render(
            Context({
                'show': reservation.occurrence.show,
                'ticket': reservation,
                'settings': settings,
            }))

        email = EmailMessage(
            subject='Tickets reserved for ' + reservation.occurrence.show.name,
            body=email_html,
            to=[reservation.email_address],
            from_email="boxoffice@newtheatre.org.uk"
        )
        email.content_subtype = 'html'

        if settings.ACTUALLY_SEND_MAIL:
            email.send()

    def create(self, request):
        if request.method == 'POST':
            defaults = request.POST.dict()
            defaults['occurrence'] = get_object_or_404(models.Occurrence, id=defaults.pop('occurrence_id'))

            reservation = models.Ticket(**defaults)

            if defaults['occurrence'].date < datetime.date.today():
                # TODO make nice errors
                # Show is in the past
                return Response({"error": "Show is in the past"}, status=status.HTTP_400_BAD_REQUEST)

            if defaults['occurrence'].maximum_sell < (defaults['occurrence'].tickets_sold() +
                                                      int(request.POST.get('quantity'))):
                # TODO make nice errors
                # Show is sold out
                return Response({"error": "Show is sold out"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                defaults.pop('quantity')
                tick = models.Ticket.objects.filter(**defaults).order_by('-stamp')[0]

                if tick.stamp > datetime.datetime.now() - datetime.timedelta(minutes=5):
                    # TODO make nice errors
                    return Response({"error": "Wait a bit please"},
                                    status=status.HTTP_400_BAD_REQUEST)
                    # Tried to book too quickly
                else:
                    reservation.save()
            except IndexError:
                reservation.save()

            self.send_mail(reservation=reservation)

            serializer = self.serializer_class(reservation, read_only=True)

            return Response(serializer.data)
        else:
            # TODO make nice errors
            return Response({"error": "bad request"}, status=status.HTTP_400_BAD_REQUEST)  # Not a post

    @action(detail=False, url_name='cancel_booking', url_path='cancel', methods=['POST'])
    def cancel_reservation(self, request):
        if request.method == 'POST':
            reservation = get_object_or_404(models.Ticket, unique_code=request.POST.get('ticket_unique_code', None))

            reservation.cancelled = True
            reservation.save()

            # TODO send cancellation email

            serializer = self.serializer_class(reservation, read_only=True)

            return Response(serializer.data)
        else:
            # TODO make nice errors
            return Response({"error": "bad request"}, status=status.HTTP_400_BAD_REQUEST)  # Not a post
