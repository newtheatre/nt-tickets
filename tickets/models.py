from django.db import models

# Create your models here.

class Ticket_Type(models.Model):
	name=models.CharField(max_length=30)
	price=models.DecimalField(max_digits=4, decimal_places=2)
	def __unicode__(self):
		return self.name+" L"+str(self.price)

class Show(models.Model):
	name=models.CharField(max_length=30)
	location=models.CharField(max_length=30, default='Theatre')
	def __unicode__(self):
		return self.name;

class Occurrence(models.Model):
	show=models.ForeignKey(Show)
	date=models.DateField()
	time=models.TimeField()
	maximum_sell=models.PositiveIntegerField()
	hours_til_close=models.IntegerField(default=3)
	tickets_available=models.ManyToManyField(Ticket_Type)

	def __unicode__(self):
		return self.show.name+" on "+str(self.date)+" at "+str(self.time)

class Ticket(models.Model):	
	occurrence=models.ForeignKey(Occurrence)
	stamp=models.DateTimeField(auto_now=True)
	person_name=models.CharField(max_length=40)
	email_address=models.EmailField(max_length=40)
	type=models.ForeignKey(Ticket_Type)