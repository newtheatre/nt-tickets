# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
import configuration.customise as config
from django.utils.encoding import python_2_unicode_compatible

from tickets.models import *


class PricingBase(models.Model):

    class Meta:
        abstract =True

    concession_price = models.DecimalField(max_digits=6, decimal_places=2, default=config.CONCESSION_PRICE[0])
    public_price = models.DecimalField(max_digits=6, decimal_places=2, default=config.PUBLIC_PRICE[0])
    member_price = models.DecimalField(max_digits=6, decimal_places=2, default=config.MEMBER_PRICE[0])


@python_2_unicode_compatible
class SeasonTicketPricing(models.Model):

    class Meta:
        verbose_name = 'Season Ticket Pricing'
        verbose_name_plural = 'Season Ticket Pricing'

    season_ticket_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
      s = 'Season Ticket Pricing'
      return s

    def save(self, *args, **kwargs):
      super(SeasonTicketPricing, self).save(*args, **kwargs)


@python_2_unicode_compatible
class InHousePricing(PricingBase):

    class Meta:
        verbose_name = 'In House Pricing'
        verbose_name_plural = 'In House Pricing'

    matinee_freshers_price = models.DecimalField(max_digits=6, decimal_places=2, default=config.MATINEE_FRESHERS_PRICE[0])
    matinee_freshers_nnt_price = models.DecimalField(max_digits=6, decimal_places=2, default=config.MATINEE_FRESHERS_NNT_PRICE[0])

    def __str__(self):
      s = 'In House Pricing'
      return s

    def save(self, *args, **kwargs):
        super(InHousePricing, self).save(*args, **kwargs)


@python_2_unicode_compatible
class FringePricing(models.Model):

    class Meta:
        verbose_name = 'Fringe Pricing'
        verbose_name_plural = 'Fringe Pricing'

    fringe_price = models.DecimalField(max_digits=6, decimal_places=2, default=config.FRINGE_PRICE[0])

    def __str__(self):
      s = 'Fringe Pricing'
      return s

    def save(self, *args, **kwargs):
        super(FringePricing, self).save(*args, **kwargs)


@python_2_unicode_compatible
class ExternalPricing(PricingBase):

    class Meta:
        verbose_name = 'External Pricing'
        verbose_name_plural = 'External Pricing'

    show = models.ForeignKey(Show)

    matinee_freshers_price = models.DecimalField(max_digits=6, decimal_places=2, default=config.MATINEE_FRESHERS_PRICE[0])
    matinee_freshers_nnt_price = models.DecimalField(max_digits=6, decimal_places=2, default=config.MATINEE_FRESHERS_NNT_PRICE[0])

    allow_season_tickets = models.BooleanField(default=True)
    allow_fellow_tickets = models.BooleanField(default=True)
    allow_half_matinee = models.BooleanField(default=True)
    allow_half_nnt_matinee = models.BooleanField(default=True)

    def __str__(self):
      s = 'Pricing for: ' + self.show.name
      return s

    def save(self, *args, **kwargs):
        super(ExternalPricing, self).save(*args, **kwargs)


@python_2_unicode_compatible
class StuFFPricing(PricingBase):

    class Meta:
        verbose_name = 'StuFF Pricing'
        verbose_name_plural = 'StuFF Pricing'

    show = models.ForeignKey(Show)

    def __str__(self):
      s = 'Pricing for: '  + self.show.name
      return s

    def save(self, *args, **kwargs):
        super(StuFFPricing, self).save(*args, **kwargs)


@python_2_unicode_compatible
class StuFFEventPricing(PricingBase):

    class Meta:
        verbose_name = 'StuFF Event Pricing'
        verbose_name_plural = 'StuFF Event Pricing'

    show = models.ForeignKey(Show)

    def __str__(self):
      s = 'Pricing for: ' + self.show.name
      return s

    def save(self, *args, **kwargs):
        super(StuFFEventPricing, self).save(*args, **kwargs)
