# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from captcha.fields import ReCaptchaField
from tickets.models import *
import settings

import configuration.customise as config

import datetime


class BookingFormLanding(forms.Form):
    occurrence = forms.ChoiceField(label="Date", choices=('0','Not Loaded'))
    person_name = forms.CharField(label="Your Full Name", max_length=80)
    email_address = forms.EmailField(max_length=80)
    max_q = settings.MAX_DISCLOSURE
    quantity = forms.IntegerField(
            label="Number of Seats",
            min_value=1,
            max_value=max_q,
            required=True,
            widget=forms.Select(choices=[(i,i) for i in range(1,max_q+1)])
            )
    add_to_mailinglist = forms.BooleanField(label="Please add me to the New Theatre mailing list for updates on future plays and events.", initial = True, required=False)

    def __init__(self, *args, **kwargs):
        show = kwargs.pop('show', None)
        super(BookingFormLanding, self).__init__(*args, **kwargs)
        self.fields['occurrence'].choices = Occurrence.objects.get_available(show=show)


class ReportForm(forms.Form):
    today = datetime.date.today()
    hide_filter = today-datetime.timedelta(weeks=4)
    occurrence = forms.ModelChoiceField(queryset=Occurrence.objects.filter(date__gte=hide_filter).order_by('date','time'), label='')


class LoginForm(AuthenticationForm):
    captcha = ReCaptchaField(label='Captcha')


class CancelForm(forms.Form):
    ticket = forms.CharField(max_length=16)
    occurrence = forms.CharField(max_length=16)


class SaleForm(forms.Form):
    ticket = forms.CharField(label='Reservation', max_length=80)

    number_concession = forms.IntegerField(label="Concession Tickets " + config.CONCESSION_PRICE[1])
    number_public = forms.IntegerField(label="Public Tickets " + config.PUBLIC_PRICE[1])
    number_season = forms.IntegerField(label="Season Pass Tickets")
    number_fellow = forms.IntegerField(label="Fellow Tickets")

    def at_least_one(self):
        nc = self.cleaned_date.get('number_concession')
        np = self.cleaned_date.get('number_public')
        ns = self.cleaned_date.get('number_season')
        nf = self.cleaned_date.get('number_fellow')

        total_sale = nc + np + ns + nf

        if total_sale == 0:
            raise ValidationError("Please input at least one sale")

        return 

class ReserveForm(forms.Form):
    ticket = forms.CharField(label='Reservation', max_length=80)
