# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class Ticket_Type(models.Model):
	name=models.CharField(max_length=30)
	price=models.DecimalField(max_digits=4, decimal_places=2)
	def price_formatted(self):
		return u"£%.2f" % self.price
	def __unicode__(self):
		return self.name+" L"+str(self.price)

class Show(models.Model):
	name=models.CharField(max_length=30)
	location=models.CharField(max_length=30, default='Theatre')
	
	def all_ticket_types(self):
		ticket_types=[]
		for o in self.occurrence_set.all():
			for t in o.tickets_available.all():
				if not t in ticket_types:
					ticket_types.append(t)
		return ticket_types

	def __unicode__(self):
		return self.name;

class Occurrence(models.Model):
	show=models.ForeignKey(Show)
	date=models.DateField()
	time=models.TimeField()
	maximum_sell=models.PositiveIntegerField()
	hours_til_close=models.IntegerField(default=3)
	tickets_available=models.ManyToManyField(Ticket_Type)

	def day_formatted(self):
		return self.date.strftime('%A')
	def time_formatted(self):
		return self.time.strftime('%-I%p').lower()
	def datetime_formatted(self):
		return self.date.strftime('%A %d %B ')+self.time.strftime('%-I%p').lower()

	def __unicode__(self):
		return self.show.name+" on "+str(self.date)+" at "+str(self.time)

class Ticket(models.Model):	
	occurrence=models.ForeignKey(Occurrence)
	stamp=models.DateTimeField(auto_now=True)
	person_name=models.CharField(max_length=80)
	email_address=models.EmailField(max_length=80)
	type=models.ForeignKey(Ticket_Type)

