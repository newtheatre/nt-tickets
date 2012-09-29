from django import forms
from tickets.models import *

class OccurrenceChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    return "%s" % obj.datetime_formatted()

class BookingFormLanding(forms.Form):
	person_name=forms.CharField(max_length=80)
	email_address=forms.EmailField(max_length=80)
	occurrence=OccurrenceChoiceField(queryset=None,empty_label="No Occurrences")

	def __init__(self, *args, **kwargs):
		show = kwargs.pop('show', None)
		super(BookingFormLanding, self).__init__(*args, **kwargs)
		self.fields['occurrence'].queryset = Occurrence.objects.filter(show=show.id)
		self.fields['occurrence'].empty_label=None

class BookingFormOccurrence(forms.Form):

	def __init__(self, *args, **kwargs):
		show = kwargs.pop('show', None)
		ticket_types = kwargs.pop('ticket_types', None)
		super(BookingFormOccurrence, self).__init__(*args, **kwargs)

		for t in ticket_types:
			label = t.name+" "+t.price_formatted()
			self.fields[str(t.id)] = forms.IntegerField(max_value=10, min_value=0, initial=0, label=label)

class ReportForm(forms.Form):
	occurrence=forms.ModelChoiceField(queryset=Occurrence.objects.all())