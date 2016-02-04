# -*- coding: utf-8 -*-
from django.db import models
import datetime

from PIL import Image
from stdimage.models import StdImageField
from stdimage.utils import UploadToClassNameDir
from StringIO import StringIO
from markdown2 import Markdown

from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.core.validators import *

from tickets.func import rand_16

import configuration.customise as config

from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(
        max_length=50,
        help_text='Shows up on pages.'
        )
    slug = models.SlugField(
        help_text='Will be used in class names, so you can style categories differently.'
        )
    sort = models.IntegerField(
        help_text='Low to high, sorts the sidebar.',
        validators=[
                MinValueValidator(6, 'Minimum values is 6')
            ]
        )

    def __str__(self): 
        return self.name


@python_2_unicode_compatible
class Show(models.Model):
    class Meta:
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'

    name = models.CharField(max_length=64)

    slug = models.SlugField(
                    blank=True,
                    help_text='Used in the URL of the detail page, leave blank to auto-generate.'
                    )

    location = models.CharField(
                    max_length=30,
                    default=config.DEFAULT_LOCATION,
                    help_text='Will show up alongside show, you can hide this with CSS if needed.'
                    )

    description = models.TextField(
                    help_text='A short description, one paragraph only.'
                    )

    long_description = models.TextField(
                    blank=True,
                    help_text='Shows up on the detail page, this field is written in Markdown. ' +
                    '(See <a href="http://www.darkcoding.net/software/markdown-quick-reference/">Markdown reference</a> for reference.'
                    )

    poster = StdImageField(
                    upload_to=UploadToClassNameDir(),
                    blank=True, null=True,
                    help_text='Upload a large image, we will automatically create smaller versions to use.',
                    variations={
                        'poster_wall': (126, 178),
                        'poster_page': (256, 362),
                        'poster_tiny': (50, 71),
                        }
                    )

    start_date = models.DateField()
    end_date = models.DateField()

    category = models.ForeignKey('Category')

    def is_current(self):
        today = datetime.date.today()
        if today > self.end_date:
            return False
        else:
            return True

    def show_sold_out(self):
        if self.occurrence_set.count() > 0:
            for occ in self.occurrence_set.all():
                if occ.sold_out() is False:
                    return False
            return True
        else:
            return False

    # Total profit from all occurrences in a show
    def show_sales(self):
        occs = Occurrence.objects.filter(show=self)
        total = 0
        for oc in occs:
            sale = oc.total_sales()
            total += sale
        return total

    # Total number of tickets sold across all occurrences
    def total_tickets_sold_show(self):
        sale = Occurrence.objects.filter(show=self)
        total = 0
        for s in sale:
            ticket = s.total_tickets_sold()
            total += ticket
        return total

    # Total tickets reserved across all occurrences
    def total_tickets_reserved(self):
        occs = Occurrence.objects.filter(show=self)
        total = 0
        for oc in occs:
            reserve = oc.tickets_sold()
            total += reserve
        return total

    # Maximum tickets that can be reserved across a whole show
    def total_possible(self):
        occs = Occurrence.objects.filter(show=self)
        total = 0
        for oc in occs:
            maximum = oc.maximum_sell
            total += maximum
        return total

    # Does a show have any occurrences
    def has_occurrences(self):
        occs = Occurrence.objects.filter(show=self)
        if len(occs) > 0:
            return True
        else:
            return False

    def long_markdown(self):
        md = Markdown()
        return md.convert(self.long_description)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        have_orig = False
        if self.pk:
            orig = Show.objects.get(pk=self.pk)
            have_orig = True
        super(Show, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class OccurrenceManager(models.Manager):

    def get_available(self, show):
        today = datetime.date.today()
        time = datetime.datetime.now()
        occs = Occurrence.objects.filter(show=show).filter(date__gte=today).order_by('date', 'time')
        ret = []
        for oc in occs:
            combined = datetime.datetime.combine(oc.date, oc.time)
            close_time = combined - datetime.timedelta(hours=oc.hours_til_close)
            if oc.sold_out():
                break
            if oc.date <= today and time >= close_time:
                break
            else:
                ret.append(( 
                    oc.id, 
                    oc.datetime_formatted(), 
                    ))
        return ret

    def get_available_show(self, show):
        today = datetime.date.today()
        time = datetime.datetime.now()
        occs = Occurrence.objects.filter(show=show).filter(date__gte=today).order_by('date', 'time')
        ret = []
        for oc in occs:
            combined = datetime.datetime.combine(oc.date, oc.time)
            close_time = combined + datetime.timedelta(hours=3)
            if oc.date <= today and time >= close_time:
                break
            else:
                ret.append(( 
                    oc.id, 
                    oc.datetime_formatted(), 
                    oc.day_formatted(), 
                    oc.unique_code, 
                    oc.time_formatted(), 
                    oc.tickets_sold() 
                    ))
        return ret


@python_2_unicode_compatible
class Occurrence(models.Model):

    class Meta:
        verbose_name = 'Occurrence'
        verbose_name_plural = 'Occurrences'

    show = models.ForeignKey(Show)
    date = models.DateField()
    time = models.TimeField(default=config.DEFAULT_TIME)
    maximum_sell = models.PositiveIntegerField(
                default=config.DEFAULT_MAX_SELL,
                help_text='The maximum number of tickets we will allow to be reserved.'
                )

    hours_til_close = models.IntegerField(
                default=config.DEFAULT_HOURS_TIL_CLOSE,
                help_text='Hours before \'time\' that we will stop reservations being made.'
                )
    unique_code = models.CharField(max_length=16)

    objects = OccurrenceManager()

    def day_formatted(self):
        return self.date.strftime('%A')

    def time_formatted(self):
        return self.time.strftime('%-I:%M %p').lower()

    def datetime_formatted(self):
        return self.date.strftime('%A %d %B ') + \
            self.time.strftime('%-I%p').lower()

    # Total number of tickets reserved
    def tickets_sold(self):
        tickets = Ticket.objects.filter(occurrence=self).filter(cancelled=False)
        sold = 0
        for ticket in tickets:
            sold += ticket.quantity
        return sold

    # Find if all the tickets have been reserved
    def sold_out(self):
        if self.tickets_sold() >= self.maximum_sell:
            return True
        else:
            return False

    # Total tickets sold
    def total_tickets_sold(self):
        sale = Sale.objects.filter(occurrence=self)
        sold = 0
        for s in sale:
            sold += s.number
        return sold

    # Returns the total profit from ticket sales
    def total_sales(self):
        sale = Sale.objects.filter(occurrence=self)
        sold = 0
        for s in sale:
            sold += s.price
        return sold

    def member_tally(self):
        sale = Sale.objects.filter(occurrence=self)
        member = 0
        for s in sale:
            if s.number_member > 0:
                member += s.number_member
        return member

    def concession_tally(self):
        sale = Sale.objects.filter(occurrence=self)
        concession = 0
        for s in sale:
            if s.number_concession > 0:
                concession += s.number_concession
        return concession

    def public_tally(self):
        sale = Sale.objects.filter(occurrence=self)
        public = 0
        for s in sale:
            if s.number_public > 0:
                public += s.number_public
        return public

    def season_tally(self):
        sale = Sale.objects.filter(occurrence=self)
        season = 0
        for s in sale:
            if s.number_season > 0:
                season += s.number_season
        return season

    def season_sale_tally(self):
        sale = Sale.objects.filter(occurrence=self)
        season_sale = 0
        for s in sale:
            if s.number_season_sale > 0:
                season_sale += s.number_season_sale
        return season_sale

    def fellow_tally(self):
        sale = Sale.objects.filter(occurrence=self)
        fellow = 0
        for s in sale:
            if s.number_fellow > 0:
                fellow += s.number_fellow
        return fellow

    def fringe_tally(self):
        sale = Sale.objects.filter(occurrence=self)
        fringe = 0
        for s in sale:
            if s.number_fringe > 0:
                fringe += s.number_fringe
        return fringe

    def matinee_freshers_tally(self):
        sale = Sale.objects.filter(occurrence=self)
        matinee_freshers = 0
        for s in sale:
            if s.number_matinee_freshers > 0:
                matinee_freshers += s.number_matinee_freshers
        return matinee_freshers

    def matinee_freshers_nnt_tally(self):
        sale = Sale.objects.filter(occurrence=self)
        matinee_freshers_nnt = 0
        for s in sale:
            if s.number_matinee_freshers_nnt > 0:
                matinee_freshers_nnt += s.number_matinee_freshers_nnt
        return matinee_freshers_nnt

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = rand_16()
        super(Occurrence, self).save(*args, **kwargs)
        self.show.save()

    def __str__(self):
        return self.show.name + " on " + str(self.day_formatted()) + " at " + str(self.time_formatted())


class TicketManager(models.Manager):

    def get_collected(self, occurrence):
        ticket = Ticket.objects.filter(collected='True', occurrence=occurrence)
        quantity = 0

        for tick in ticket:
            quantity += tick.quantity

        return quantity


@python_2_unicode_compatible
class Ticket(models.Model):

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    occurrence = models.ForeignKey(Occurrence)
    stamp = models.DateTimeField(auto_now=True)
    person_name = models.CharField(max_length=80)
    email_address = models.EmailField(max_length=80)
    quantity = models.IntegerField(default=1)
    cancelled = models.BooleanField(default=False)
    collected = models.BooleanField(default=False)
    unique_code = models.CharField(max_length=16)
    objects = TicketManager()

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = rand_16()
        super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return self.occurrence.show.name + \
            " on " + str(self.occurrence.date) + \
            " at " + str(self.occurrence.time) + \
            " for " + self.person_name


class SaleManager(models.Manager):

    def sold_not_reserved(self, occurrence):
        sale = Sale.objects.filter(occurrence=occurrence, ticket='None')
        number = 0

        for s in sale:
            number += s.number

        return number

class Sale(models.Model):

    class Meta:
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'

    objects=SaleManager()

    occurrence = models.ForeignKey(Occurrence)
    ticket = models.CharField(max_length=80)

    stamp = models.DateTimeField(auto_now=True)
    unique_code = models.CharField(max_length=16)

    price = models.DecimalField(max_digits=6, decimal_places=2)
    number = models.IntegerField()

    number_concession = models.IntegerField(default=0)
    number_member = models.IntegerField(default=0)
    number_public = models.IntegerField(default=0)
    number_season = models.IntegerField(default=0)
    number_season_sale = models.IntegerField(default=0)
    number_fellow = models.IntegerField(default=0)
    number_fringe = models.IntegerField(default=0)
    number_matinee_freshers = models.IntegerField(default=0)
    number_matinee_freshers_nnt = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = rand_16()
        super(Sale, self).save(*args, **kwargs)
