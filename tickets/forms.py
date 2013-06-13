from django import forms
from tickets.models import *

import datetime

class BookingFormLanding(forms.Form):
	occurrence=forms.ChoiceField(label="Date",choices=('0','Not Loaded'))
	person_name=forms.CharField(label="Your Full Name",max_length=80)
	email_address=forms.EmailField(max_length=80)
	max_q=8
	quantity=forms.IntegerField(label="Number of Seats",min_value=1,max_value=max_q,required=True,widget=forms.Select(choices=  [ (i,i) for i in range(1,max_q+1) ]) )

	def __init__(self, *args, **kwargs):
		show = kwargs.pop('show', None)
		super(BookingFormLanding, self).__init__(*args, **kwargs)
		self.fields['occurrence'].choices = Occurrence.objects.get_avaliable(show=show)

class ReportForm(forms.Form):
	occurrence=forms.ModelChoiceField(queryset=Occurrence.objects.all())