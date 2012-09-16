from django import forms
from tickets.models import *

class OccurrenceChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    return "%s" % str(obj.date)

class BookingFormLanding(forms.Form):
	person_name=forms.CharField(max_length=80)
	email_address=forms.EmailField(max_length=80)
	occurrence=OccurrenceChoiceField(queryset=None,empty_label="No Occurrences")

	def __init__(self, *args, **kwargs):
		show = kwargs.pop('show', None)
		super(BookingFormLanding, self).__init__(*args, **kwargs)
		self.fields['occurrence'].queryset = Occurrence.objects.filter(show=show.id)
		self.fields['occurrence'].empty_label=None

class BookingFormOccurrences(forms.Form):

	def __init__(self,*args,**kwargs):
		ticket_types = kwargs.pop('ticket_types', None)
		super(BookingFormOccurrences, self).__init__(*args, **kwargs)

		for t in ticket_types:
			self.fields['ticket_type_{id}'.format(id=t.id)] = forms.PositiveIntegerField(max_value=5)

