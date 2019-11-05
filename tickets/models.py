# -*- coding: utf-8 -*-
from django.db import models
import datetime

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

from collections import Counter 


@python_2_unicode_compatible
class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        unique_together = ('name', 'sort',)

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
class ContentWarning(models.Model):
    class Meta:
        verbose_name = 'Content Warning'
        verbose_name_plural = 'Content Warnings'

    title = models.CharField(
        max_length = 100,
        help_text = 'The name of the warning'
    )
    icon = models.CharField(
        max_length = 50,
        help_text = 'An icon code, from this list: https://material.io/icons/',
        blank=True,
    )

    category_choices = (
        ('1', 'Technical Effects'),
        ('2', 'Content'),
    )
    category = models.CharField(
        max_length = 50,
        choices = category_choices,
        default = '2'
    )

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Show(models.Model):

    class Meta:
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'
        unique_together = ('name', 'start_date', 'end_date')

    name = models.CharField(max_length=255)

    is_draft = models.BooleanField(default=False,
        help_text="Tick to hide from all listings, etc. Useful for being able to add the new season as draft until launch date.")

    slug = models.SlugField(
        blank=True,
        max_length=255,
        help_text='Used in the URL of the detail page, leave blank to auto-generate.'
    )

    location = models.CharField(
        max_length=30,
        default=config.DEFAULT_LOCATION,
        help_text='Will show up alongside show, you can hide this with CSS if needed.'
    )

    runtime = models.IntegerField(
        blank=True, null=True,
        help_text = 'Show running time in minutes, without interval time.'
    )

    interval_number = models.IntegerField(
        default = 0,
        help_text = 'Number of intervals the show has, typically 0 or 1.'
    )

    description = models.TextField(
        help_text='A short description',
    )

    long_description = models.TextField(
        blank=True,
        help_text='Shows up on the detail page, this field is written in Markdown. ' +
        '(See <a href="http://www.darkcoding.net/software/markdown-quick-reference/">Markdown reference</a> for reference).'
    )

    poster = StdImageField(
        upload_to=UploadToClassNameDir(),
        blank=True, null=True,
        help_text='Upload a large image, we will automatically create smaller versions to use.',
        variations={
            'poster_wall': (126, 178),
            'poster_page': (256, 362),
            'poster_tiny': (50, 71),
            'poster_whatson': (500, 750),
        }
    )

    programme = models.URLField(
        blank=True, null=True,
        help_text='Link to a page or PDF hosting a programme. Try hosting it on Google Drive or <a href="https://github.com/newtheatre/history-project/tree/master/assets/for_shows" target="_blank">Github</a>.'
    )

    no_warnings = models.BooleanField(
        default=False,
        help_text='Select True if a show has no content warnings.'
    )

    warnings_technical = models.ManyToManyField(
        'ContentWarning', 
        blank=True,
        limit_choices_to={'category': '1'},
        related_name='warnings_technical',
        verbose_name = 'Technical Warnings'
    )
    warnings_action = models.ManyToManyField(
        'ContentWarning',
        blank=True,
        limit_choices_to={'category': '2'},
        related_name = 'warnings_action',
        verbose_name = 'Scenes of...',
    )
    warnings_dialogue = models.ManyToManyField(
        'ContentWarning',
        blank=True,
        limit_choices_to={'category': '2'},
        related_name = 'warnings_dialogue',
        verbose_name = 'Discussions / themes of...',
    )

    warnings_notes = models.TextField(
        blank=True,
        help_text = "Description of any content warnings. Visible to Front of House only."
    )

    start_date = models.DateField()
    end_date = models.DateField()

    category = models.ForeignKey('Category')

    allow_reservations = models.BooleanField(default=True)

    external_link = models.URLField(
        blank=True,
        help_text = "Link to an external booking website; overrides NT reservation capability. Don't forget the 'http://'!",
    )

    def date_formatted(self):
        return self.start_date.strftime('%A %d %B %Y')

    def is_current(self):
        return datetime.date.today() <= self.end_date

    def is_current_show(self):
        return (datetime.date.today() - datetime.timedelta(days=1)) <= self.end_date

    def show_sold_out(self):
        if self.has_occurrences():
            occ_max_sell_count = 0
            ticket_count = 0
            for occ in self.occurrence_set.all():
                ticket_count += occ.tickets_sold()
                occ_max_sell_count += occ.maximum_sell

            return ticket_count >= occ_max_sell_count
        else:
            return False

    def booking_closed(self):
        if len(Occurrence.objects.get_available(self)) > 0:
            return False
        else:
            return True

    # Get sale data for shows
    def get_sale_data(self):
        occs = Occurrence.objects.filter(show=self)
        totals = {'show_sales': 0, 'total_sold': 0, 'total_reserved': 0, 'total_possible': 0}
        for oc in occs:
            totals['show_sales'] += oc.get_ticket_data()['total_profit']
            totals['total_sold'] += oc.get_ticket_data()['total_sold']
            totals['total_reserved'] += oc.tickets_sold()
            totals['total_possible'] += oc.maximum_sell
        return totals

    # Does a show have any occurrences
    def has_occurrences(self):
        return Occurrence.objects.filter(show=self).count() > 0

    def occurrences_formatted(self):
        occ_list = Occurrence.objects.filter(show=self).order_by('date').order_by('time')
        time_list = []
        date_list = []
        for o in occ_list:
            time_list.append(o.time)
            date_list.append(o.date)

        # One-shot
        if occ_list.count() <= 1:
            return occ_list[0].time_formatted()
        # All shows at the same time
        elif all (x==time_list[0] for x in time_list):
            return 'All performances at ' + occ_list[0].time_formatted()
        # Two shows, each at different times
        elif occ_list.count() == 2:
            # 1. The shows are the same day
            if all (x==date_list[0] for x in date_list):
                return occ_list[0].time_formatted() + ' and ' + occ_list[1].time_formatted()
            # 2. Two shows at different times on different days 
            else:
                return occ_list[0].day_formatted() + ' at ' + occ_list[0].time_formatted() \
                    + '; ' + occ_list[1].day_formatted() + ' at ' + occ_list[1].time_formatted()
        else: 
            # Many shows
            ## Only one odd one out
            if len(set(time_list)) == 2:
                odd_one_out = [i for i, n in Counter(time_list).iteritems() if n == 1]
                if not odd_one_out: 
                    return 'Various performance times, click "Reserve tickets" for details.'
                odd_one_out = occ_list.get(time=odd_one_out[0])
                # Get the usual time, making sure not to accidentally select the 'one off' time
                if time_list[0] == odd_one_out.time:
                    majority_time = time_list[1]
                else:
                    majority_time = time_list[0]
                majority = occ_list.filter(time=majority_time)[0]
                # Get the occurrences with the majority time; just need one of them 

                # Is the odd one out an additional performance or a distinct one?
                # eg., Wed-Sat evenings plus Sat Mat
                # Or, Wed-Fri evenings plus Sat Mat 
                if len(set(date_list)) == len(date_list):
                    # Distinct performance 
                    return 'Performances at ' + majority.time_formatted() + \
                        ', with ' + odd_one_out.day_formatted() + "'s at " + odd_one_out.time_formatted()
                else:
                    # Additional performance 
                    return 'Performances at ' + majority.time_formatted() + \
                        ', plus ' + odd_one_out.day_formatted() + ' at ' + odd_one_out.time_formatted()
            else: 
                return 'Various performance times, click "Reserve tickets" for details.'

    def long_markdown(self):
        return Markdown().convert(self.long_description)

    def clean(self, *args, **kwargs): 
        cleaned_data = super(Show, self).clean(*args, **kwargs)

        # Check to see if dates require the use of timetravel
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError(('Unless you have invented time travel, a show cannot end before it has started'), code='invalid_show_dates')

        return cleaned_data

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
        occs = Occurrence.objects.filter(show=show).filter(
            date__gte=today).order_by('date', 'time')
        ret = []
        for oc in occs:
            combined = datetime.datetime.combine(oc.date, oc.time)
            close_time = combined - datetime.timedelta(hours=oc.hours_til_close)
            if not oc.sold_out() and not (oc.date <= today and time >= close_time):
                ret.append((
                    oc.id,
                    oc.datetime_formatted(),
                ))
        return ret

    def get_available_show(self, show):
        today = datetime.date.today()
        time = datetime.datetime.now()
        occs = Occurrence.objects.filter(show=show).filter(
            date__gte=today).order_by('date', 'time')
        ret = []
        for oc in occs:
            combined = datetime.datetime.combine(oc.date, oc.time)
            close_time = combined + datetime.timedelta(hours=3)
            if oc.date <= today and time >= close_time:
                pass
            else:
                ret.append((
                    oc.id,
                    oc.datetime_formatted(),
                    oc.day_date(),
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
        unique_together = ('show', 'date', 'time')

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
            self.time.strftime('%-I:%M %p').lower()

    def day_date(self):
        return self.date.strftime('%A %d %B ')

    # Total number of tickets reserved
    def tickets_sold(self):
        tickets = Ticket.objects.filter(occurrence=self, cancelled=False)
        sold = 0
        for ticket in tickets:
            sold += ticket.quantity
        return sold

    # Find if all the tickets have been reserved
    def sold_out(self):
        return self.tickets_sold() >= self.maximum_sell

    # Total tickets sold
    def get_ticket_data(self):
        sale = Sale.objects.filter(occurrence=self)
        sold = {'total_sold': 0, 'total_profit': 0}
        for s in sale:
            sold['total_sold'] += s.number
            sold['total_profit'] += s.price
        return sold

    # Get tallys from sale fields
    def get_tally(self, field):
        sale = Sale.objects.filter(occurrence=self)
        tally = 0
        for s in sale:
            num = getattr(s, 'number_' + str(field))
            if num > 0:
                tally += num
        return tally

    def clean(self, *args, **kwargs): 
        cleaned_data = super(Occurrence, self).clean(*args, **kwargs)

        # Check to see if the date is within the show dates
        if self.date:
            if self.date > self.show.end_date or self.date < self.show.start_date:
                raise ValidationError(('Please enter a date within the dates of the show'), code='invalid_occ_date')

        return cleaned_data

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
    # Initial quantity is used when not the full number of tickets reserved is bought
    # It will be used in the future for more stats on the sale reports page
    initial_quantity = models.IntegerField(default=0)
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

    objects = SaleManager()

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
    number_season_sale_nnt = models.IntegerField(default=0)
    number_fellow = models.IntegerField(default=0)
    number_fringe = models.IntegerField(default=0)
    number_matinee_freshers = models.IntegerField(default=0)
    number_matinee_freshers_nnt = models.IntegerField(default=0)

    number_stuff = models.IntegerField(default=0)
    number_festival = models.IntegerField(default=0)
    number_festival_sales = models.IntegerField(default=0)
    number_day = models.IntegerField(default=0)
    number_day_sales = models.IntegerField(default=0)
    number_performer = models.IntegerField(default=0)
    number_performer_sales = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = rand_16()
        super(Sale, self).save(*args, **kwargs)
