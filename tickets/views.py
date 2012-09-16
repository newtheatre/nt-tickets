# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.formtools.wizard.views import SessionWizardView

from tickets.models import Show
from tickets.forms import BookingFormLanding

def defaultFNI(request):
	html="<html><body><h1>nt_tickets</h1><p>Function not implemented.</p></body></html>"
	return HttpResponse(html)

def book_landing(request, show_id):
	show = Show.objects.get(id=show_id)
	ticket_types=show.all_ticket_types()

	print ticket_types

	if request.method == 'POST': # If the form has been submitted...
		form = BookingFormLanding(request.POST, show=show) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			print "form OK"
			request.session['person_name']=form.cleaned_data['person_name']
			request.session['email_address']=form.cleaned_data['email_address']
			request.session['occurrence']= form.cleaned_data['occurrence']
			return HttpResponseRedirect('./occurrence') # Redirect after POST
	else:
		form = BookingFormLanding(show=show) # An unbound form

	return render(request, 'book_landing.html', {
		'form': form,
		'ticket_types':ticket_types,
	})

def book_occurrence(request,show_id):
	if request.method=='POST':
		pass
	else:
		return HttpResponse(request.session['occurrence'].maximum_sell)