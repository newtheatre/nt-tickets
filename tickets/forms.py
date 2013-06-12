from django import forms
from tickets.models import *

class OccurrenceChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    return "%s" % obj.datetime_formatted()

class BookingFormLanding(forms.Form):
	occurrence=OccurrenceChoiceField(queryset=None,empty_label="No Occurrences")
	person_name=forms.CharField(max_length=80)
	email_address=forms.EmailField(max_length=80)
	max_q=8
	quantity=forms.IntegerField(label="Quantity",min_value=1,max_value=max_q,required=True,widget=forms.Select(choices=  [ (i,i) for i in range(1,max_q+1) ]) )

	def __init__(self, *args, **kwargs):
		show = kwargs.pop('show', None)
		super(BookingFormLanding, self).__init__(*args, **kwargs)
		self.fields['occurrence'].queryset = Occurrence.objects.filter(show=show.id)
		self.fields['occurrence'].empty_label=None

class ReportForm(forms.Form):
	occurrence=forms.ModelChoiceField(queryset=Occurrence.objects.all())