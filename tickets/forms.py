from django import forms
from tickets.models import *

import datetime

class OccurrenceChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    return "%s" % obj.datetime_formatted()

class BookingFormLanding(forms.Form):
	occurrence=OccurrenceChoiceField(label="Date",queryset=None,empty_label="No Occurrences")
	person_name=forms.CharField(label="Your Full Name",max_length=80)
	email_address=forms.EmailField(max_length=80)
	max_q=8
	quantity=forms.IntegerField(label="Number of Seats",min_value=1,max_value=max_q,required=True,widget=forms.Select(choices=  [ (i,i) for i in range(1,max_q+1) ]) )

	def __init__(self, *args, **kwargs):
		show = kwargs.pop('show', None)
		super(BookingFormLanding, self).__init__(*args, **kwargs)
		today=datetime.date.today()
		self.fields['occurrence'].queryset = Occurrence.objects.get_avaliable()
		self.fields['occurrence'].empty_label=None

class ReportForm(forms.Form):
	occurrence=forms.ModelChoiceField(queryset=Occurrence.objects.all())