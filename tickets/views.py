# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context

from django.views.generic.list import ListView

from tickets.models import *
from tickets.forms import *

import datetime
import settings

def defaultFNI(request):
    html="<html><body><h1>nt_tickets</h1><p>Function not implemented.</p></body></html>"
    return HttpResponse(html)

def book_landing(request, show_id):
    show = Show.objects.get(id=show_id)
    if show.is_current()==False:
        return HttpResponseRedirect('./error/')
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
            occ_id=form.cleaned_data['occurrence']
            t.occurrence = Occurrence.objects.get(pk=occ_id)
            if t.occurrence.date<datetime.date.today():
                return HttpResponseRedirect('./error/')
            t.quantity = form.cleaned_data['quantity']
            if t.occurrence.maximum_sell<(t.occurrence.tickets_sold()+t.quantity):
                return HttpResponseRedirect('./error/?err=sold_out')

            t.save()
            request.session["ticket"] = t
            
            send_mail('Ticket Confirmation', get_template('email/confirm.html').render(
                Context({
                    'show':show,
                    'ticket':t,    
                })),
                'boxoffice@fullaf.com', [t.email_address], fail_silently=False)

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
    ticket = request.session["ticket"]
    
    return render(request, 'book_finish.html', {
        'show':show, 'ticket':ticket,
    })

def book_error(request,show_id):
    if 'err' in request.GET:
        err=request.GET['err']
    else: err=None
    return render(request, 'book_error.html', {'err':err})

def list(request):
    shows=Show.objects.all()

    return render(request, 'list.html', {
        'shows':shows
    })

class OrderedListView(ListView):
    def get_queryset(self):
        return super(OrderedListView, self).get_queryset().order_by(self.order_by)

class ListShows(OrderedListView):
    model=Show
    template_name='list_shows.html'
    context_object_name='shows'
    order_by='start_date'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ListShows, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['settings'] = settings
        return context
    def get_queryset(self):
        today=datetime.date.today()
        return super(ListShows, self).get_queryset().filter(end_date__gte=today)

def sidebar(request):
    categories=Category.objects.all().exclude(sort=0).order_by('sort')
    today=datetime.date.today()
    limit=today+datetime.timedelta(weeks=3)
    current_shows=[]
    for category in categories:
        shows=Show.objects.filter(category=category).filter(end_date__gte=today).order_by('end_date').filter(start_date__lte=limit)
        if len(shows)>0:
            current_shows.append(shows[0])
    return render(request, 'sidebar.html', {'shows':current_shows, 'settings':settings})

def cancel(request, ref_id):
    ticket=get_object_or_404(Ticket, unique_code=ref_id)
    if request.POST.get("id", "")==ticket.unique_code:
        ticket.cancelled=True
        ticket.save()
        cancelled=True
        already_cancelled=False
    elif ticket.cancelled==True:
        already_cancelled=True
        cancelled=False
    else:
        cancelled=False
        already_cancelled=False

    return render(request, 'cancel.html', {'ticket':ticket, 'cancelled':cancelled,'already_cancelled':already_cancelled}) 

