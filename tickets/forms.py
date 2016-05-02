# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from tickets.models import *
import settings

import configuration.customise as config

import datetime


class BookingFormLanding(forms.Form):
    occurrence = forms.ChoiceField(label="Date", choices=('0', 'Not Loaded'))
    person_name = forms.CharField(label="Your Full Name", max_length=80)
    email_address = forms.EmailField(max_length=80)
    max_q = settings.MAX_DISCLOSURE
    quantity = forms.IntegerField(
        label="Number of Seats",
        min_value=1,
        max_value=max_q,
        required=True,
        widget=forms.Select(choices=[(i, i) for i in range(1, max_q + 1)])
    )
    add_to_mailinglist = forms.BooleanField(
        label="Please add me to the New Theatre mailing list for updates on future plays and events.", initial=True, required=False)

    def __init__(self, *args, **kwargs):
        show = kwargs.pop('show', None)
        super(BookingFormLanding, self).__init__(*args, **kwargs)
        self.fields['occurrence'].choices = Occurrence.objects.get_available(show=show)


class ReportForm(forms.Form):
    today = datetime.date.today()
    hide_filter = today - datetime.timedelta(weeks=4)
    occurrence = forms.ModelChoiceField(queryset=Occurrence.objects.filter(
        date__gte=hide_filter).order_by('date', 'time'), label='')


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=80)
    password = forms.CharField(max_length=80)


class CancelForm(forms.Form):
    ticket = forms.CharField(max_length=16)
    occurrence = forms.CharField(max_length=80)


class DownloadForm(forms.Form):
    occurrence = forms.CharField(max_length=16)


# Admin-Frontend Forms
class SaleForm(forms.Form):

    ticket = forms.CharField(label='Reservation', max_length=80)
    unique_ticket = forms.CharField(max_length=16)

    try:
        season_price = SeasonTicketPricing.objects.get(id=1).season_ticket_price
    except:
        season_price = 0

    number_concession = forms.IntegerField(label="Concession Tickets " +
                                           config.CONCESSION_PRICE[1])

    number_member = forms.IntegerField(label="Member Tickets " +
                                       config.MEMBER_PRICE[1])

    number_public = forms.IntegerField(label="Public Tickets " +
                                       config.PUBLIC_PRICE[1])

    number_season = forms.IntegerField(label="Season Pass Tickets")

    number_season_sales = forms.IntegerField(label="Season Pass Ticket Sales £" +
                                             str(season_price))

    number_fellow = forms.IntegerField(label="Fellow Tickets")

    number_fringe = forms.IntegerField(label="Fringe Tickets " +
                                       config.FRINGE_PRICE[1])

    number_matinee_freshers = forms.IntegerField(label="Matinee Fresher Tickets " +
                                                 config.MATINEE_FRESHERS_PRICE[1])

    number_matinee_freshers_nnt = forms.IntegerField(label="Matinee Member Fresher Tickets " +
                                                     config.MATINEE_FRESHERS_NNT_PRICE[1])


class ReserveForm(forms.Form):
    unique_ticket = forms.CharField(max_length=16)
