# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from django.views.generic.list import ListView

from tickets.models import *
from tickets.forms import *

import datetime

def defaultFNI(request):
	html="<html><body><h1>nt_tickets</h1><p>Function not implemented.</p></body></html>"
	return HttpResponse(html)

def book_landing(request, show_id):
	show = Show.objects.get(id=show_id)
	step=1
	total=2
	message="Tickets for performances are reserved online and payed for on collection at the box office."
	
	if request.method == 'POST': # If the form has been submitted...
		form = BookingFormLanding(request.POST, show=show) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			t=Ticket()

			t.person_name=form.cleaned_data['person_name']
			t.email_address=form.cleaned_data['email_address']
			t.show = show
			t.occurrence = form.cleaned_data['occurrence']
			t.quantity = form.cleaned_data['quantity']

			t.save()
			return HttpResponseRedirect('./thanks/') # Redirect after POST
	else:
		form = BookingFormLanding(show=show) # An unbound form

	return render(request, 'book_landing.html', {
		'form': form,
		'show':show,
		'step':step, 'total':total,
		'message':message,
	})


def book_finish(request,show_id):	
	show = Show.objects.get(id=show_id)
	
	return render(request, 'book_finish.html', {
		'show':show,
	})

def book_error(request):
	return render(request, 'book_error.html', {})

def report(request):
	report=dict()
	report['have_report']=False
	occurrence=""

	if request.method=='POST':
		form = ReportForm(request.POST)
		if form.is_valid():
			occurrence=form.cleaned_data['occurrence']
			report['tickets']=Ticket.objects.filter(occurrence=occurrence).order_by('person_name')
			report['how_many_sold']=occurrence.tickets_sold()
			report['percentage']=(report['how_many_sold']/float(occurrence.maximum_sell))*100
			report['have_report']=True
		else:
			pass		
	else:
		form=ReportForm()

	return render(request, 'report.html', {
		'form':form,
		'occurrence':occurrence,
		'report':report,
	})

def list(request):
	shows=Show.objects.all()

	return render(request, 'list.html', {
		'shows':shows
	})

class ListShows(ListView):
	model=Show
	template_name='list_shows.html'
	context_object_name='shows'