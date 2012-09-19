# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from tickets.models import Show
from tickets.forms import BookingFormLanding, BookingFormOccurrence

import datetime

def defaultFNI(request):
	html="<html><body><h1>nt_tickets</h1><p>Function not implemented.</p></body></html>"
	return HttpResponse(html)

def book_landing(request, show_id):
	show = Show.objects.get(id=show_id)
	step=1
	total=2
	message=""
	
	if request.method == 'POST': # If the form has been submitted...
		form = BookingFormLanding(request.POST, show=show) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			print "form OK"
			request.session['person_name']=form.cleaned_data['person_name']
			request.session['email_address']=form.cleaned_data['email_address']
			request.session['show']= show
			request.session['occurrence']= form.cleaned_data['occurrence']
			return HttpResponseRedirect('./occurrence/') # Redirect after POST
	else:
		form = BookingFormLanding(show=show) # An unbound form

	return render(request, 'book_landing.html', {
		'form': form,
		'show':show,
		'step':step, 'total':total,
		'message':message,
	})

def book_occurrence(request,show_id):

	if not request.session.get('show'):
		return book_error(request)
	
	show = Show.objects.get(id=show_id)
	occurrence=request.session['occurrence']
	ticket_types=occurrence.tickets_available.all()
	step=2
	total=2

	message="Enter the quantity of tickets you'd like to reserve for the "+request.session['occurrence'].day_formatted()+" "+request.session['occurrence'].time_formatted()+" performace."

	if request.method=='POST':
		form = BookingFormOccurrence(request.POST, show=show, ticket_types=ticket_types) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			print form.cleaned_data
	else:
		form = BookingFormOccurrence(show=show, ticket_types=ticket_types)

	return render(request, 'book_landing.html', {
		'form': form,
		'show':show,
		'step':step, 'total':total,
		'message':message,
	})

def book_finish(request,show_id):
	if not request.session.get('tickets'):
		return book_error(request)
	
	show = Show.objects.get(id=show_id)
	


	for sesskey in request.session.keys():
            del request.session[sesskey]

	# return render(request, 'book_finish.html', {
	# 	'show':show,
	# })

def book_error(request):
	return render(request, 'book_error.html', {
	})