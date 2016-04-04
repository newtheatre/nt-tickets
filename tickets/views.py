# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage, send_mail
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.views.decorators.cache import cache_page
import requests0 as requests
import simplejson as json
import csv

from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required

from django.views import generic
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import render_to_response

# Import models
from tickets import models, forms
from pricing import models


import configuration.customise as config
import configuration.keys as keys

import datetime
import settings

def login(request, **kwargs):
    if request.user.is_authenticated():
        next = request.GET.get('next', '/')
        return HttpResponseRedirect(request.GET.get('next', '/'))
    else:
        from django.contrib.auth.views import login

        return login(request)


def logout_view(request):
    logout(request)
    return render(request, 'registration/logout.html')


@login_required
def ShowIndex(request):

    time_filter = datetime.date.today() - datetime.timedelta(days=30)
    shows = models.Show.objects.filter(end_date__gte=time_filter).order_by('start_date')

    show_list = []

    for sh in shows:
        if sh.is_current():
            show_list.append(sh)

    paginator = Paginator(show_list, 5)
    page = request.GET.get('page')

    try:
        show = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        show = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        show = paginator.page(paginator.num_pages)

    context = {
        'show': show,
    }

    return render_to_response('show_index.html', context, context_instance=RequestContext(request)) 


@login_required
def ShowReport(request, show_name, occ_id):
    report = dict()
    show = get_object_or_404(models.Show, id=show_name)
    occurrence = models.Occurrence.objects.get_available_show(show=show_name)

    report['default_time'] = \
        config.DEFAULT_TIME.strftime('%-I:%M %p').lower()

    report['default_time_matinee'] = \
        config.DEFAULT_TIME_MATINEE.strftime('%-I:%M %p').lower()

    report['concession_price'] = config.CONCESSION_PRICE[0]
    report['member_price'] = config.MEMBER_PRICE[0]
    report['public_price'] = config.PUBLIC_PRICE[0]
    report['fringe_price'] = config.FRINGE_PRICE[0]
    report['matinee_freshers_price'] = config.MATINEE_FRESHERS_PRICE[0]
    report['matinee_freshers_nnt_price'] = config.MATINEE_FRESHERS_NNT_PRICE[0]

    report['season_price'] = models.SeasonTicketPricing.objects.get(id=1).season_ticket_price

    # If there has been an occurrnece selected
    if occ_id > '0':
        report['have_form'] = True
        occ_fin = models.Occurrence.objects.get(id=occ_id)

        report['day'] = occ_fin.day_formatted()
        report['time'] = occ_fin.time_formatted()

        report['max'] = occ_fin.maximum_sell

        report['tickets'] = models.Ticket.objects.filter(occurrence=occ_fin).order_by('person_name')

        # How many tickets have been sold so far
        report['sold'] = occ_fin.total_tickets_sold()
        # Total number of tickets reserved
        report['how_many_reserved'] = occ_fin.tickets_sold()
        # How many tickets have been collected
        report['how_many_collected'] = occ_fin.tickets_sold() - models.Ticket.objects.get_collected(occurrence=occ_fin)
        # How many un-reserved tickets are there left to sell
        report['how_many_sales_left'] = occ_fin.maximum_sell - occ_fin.tickets_sold() - models.Sale.objects.sold_not_reserved(occurrence=occ_fin)
        # Maximum amount of free tickets to sell
        report['how_many_left'] = occ_fin.maximum_sell - occ_fin.tickets_sold()

        report['total_sales'] = occ_fin.total_sales()

        report['reserve_percentage'] = (report['how_many_reserved'] / float(occ_fin.maximum_sell)) * 100
        report['sale_percentage'] = (report['sold'] / float(occ_fin.maximum_sell)) * 100

        report['reservation'] = 'None'
        report['unique_ticket'] = 'None'

        category = occ_fin.show.category
        report['category'] = category

        # In House Pricing
        if category.id == 1:
            try:
                pricing = models.InHousePricing.objects.get(id=1)
                report['pricing_error'] = False
            except ObjectDoesNotExist:
                pricing = []
                report['pricing_error'] = True

        # Fringe Pricing
        elif category.id == 2:
            try:
                pricing = models.FringePricing.objects.get(id=1)
                report['pricing_error'] = False
            except ObjectDoesNotExist:
                pricing = []
                report['pricing_error'] = True

        # External Pricing
        elif category.id == 3:
            try:
                pricing = models.ExternalPricing.objects.get(show_id=show_name)
                report['matinee_freshers_price'] = pricing.public_price / 2
                report['matinee_freshers_nnt_price'] = pricing.member_price / 2
                report['pricing_error'] = False
            except ObjectDoesNotExist:
                pricing = []
                report['pricing_error'] = True

        elif category.id == 4:
            try:
                pricing = models.StuFFPricing.objects.get(show_id=show_name)
                report['stuff_price'] = pricing.stuff_price
                report['pricing_error'] = False
            except ObjectDoesNotExist:
                pricing = []
                report['pricing_error'] = True

        else:
            pricing = []

    else:
        report['have_form'] = False
        report['pricing_error'] = False
        pricing = []

    # Testing if the show is current
    if show.is_current():
        report['current'] = True
    else:
        report['current'] = False

    S_form = forms.SaleForm

    context = {
        'report': report,
        'show': show,
        'occurrence': occurrence,
        'S_form': S_form,
        'occ_id': occ_id,
        'show_name': show_name,
        'pricing': pricing,
    }

    return render_to_response(
        'show_report.html',
        context,
        context_instance=RequestContext(request)
        )


@login_required
def SaleInputAJAX(request, show_name, occ_id):
    report = dict()

    if request.method == 'POST' and request.is_ajax():

        s = models.Sale()
        occ_fin = models.Occurrence.objects.get(id=occ_id)
        show = get_object_or_404(models.Show, id=show_name)
        s.occurrence = occ_fin
        s.ticket = request.POST.get('reservation')
        report['tickets'] = models.Ticket.objects.filter(occurrence=occ_fin).order_by('person_name')

        category = show.category

        if category.id == 1:
            pricing = models.InHousePricing.objects.get(id=1)

        # Fringe Pricing
        elif category.id == 2:
            pricing = models.FringePricing.objects.get(id=1)

        # External Pricing
        elif category.id == 3:
            pricing = models.ExternalPricing.objects.get(show_id=show_name)

        elif category.id == 4:
            pricing = models.StuFFPricing.objects.get(show_id=show_name)

        try:
            number_concession = float(request.POST.get('number_concession'))
        except:
            number_concession = float(0)

        try:
            number_member = float(request.POST.get('number_member'))
        except:
            number_member = float(0)

        try:
            number_public = float(request.POST.get('number_public'))
        except:
            number_public = float(0)

        try:
            number_season = float(request.POST.get('number_season'))
        except:
            number_season = float(0)

        try:
            number_season_sale = float(request.POST.get('number_season_sales'))
        except:
            number_season_sale = float(0)

        try:
            number_fellow = float(request.POST.get('number_fellow'))
        except:
            number_fellow = float(0)

        try:
            number_fringe = float(request.POST.get('number_fringe'))
        except:
            number_fringe = float(0)

        try:
            number_matinee_freshers = float(request.POST.get('number_matinee_freshers'))
        except:
            number_matinee_freshers = float(0)

        try:
            number_matinee_freshers_nnt = float(request.POST.get('number_matinee_freshers_nnt'))
        except:
            number_matinee_freshers_nnt = float(0)

        try:
            number_stuff = float(request.POST.get('number_stuff'))
        except:
            number_stuff = float(0)

        s.number_concession = number_concession
        s.number_member = number_member
        s.number_public = number_public
        s.number_season = number_season
        s.number_season_sale = number_season_sale
        s.number_fellow = number_fellow
        s.number_fringe = number_fringe
        s.number_matinee_freshers = number_matinee_freshers
        s.number_matinee_freshers_nnt = number_matinee_freshers_nnt
        s.number_stuff = number_stuff

        try:
            concession_sale = number_concession * float(pricing.concession_price)
        except Exception:
            concession_sale = float(0)

        try:
            member_sale = number_member * float(pricing.member_price)
        except Exception:
            member_sale = float(0)

        try:
            public_sale = number_public * float(pricing.public_price)
        except Exception:
            public_sale = float(0)

        season_sale = number_season * float(models.SeasonTicketPricing.objects.get(id=1).season_ticket_price)

        try:
            fringe_sale = number_fringe * float(pricing.fringe_price)
        except Exception:
            fringe_sale = float(0)

        try:
            matinee_fresher_sale = number_matinee_freshers * float(pricing.matinee_freshers_price)
        except Exception:
            matinee_fresher_sale = float(0)

        try:
            matinee_fresher_nnt_sale = number_matinee_freshers_nnt * float(pricing.matinee_freshers_nnt_price)
        except Exception:
            matinee_fresher_nnt_sale = float(0)

        try:
            stuff_sale = number_stuff * float(pricing.stuff_price)
        except Exception:
            stuff_sale = float(0)

        price = (
            concession_sale +
            member_sale +
            public_sale +
            season_sale +
            fringe_sale +
            matinee_fresher_sale +
            matinee_fresher_nnt_sale + 
            stuff_sale
            )

        number = (
            number_concession +
            number_member +
            number_public +
            number_fringe +
            number_matinee_freshers +
            number_matinee_freshers_nnt +
            number_season +
            number_season_sale +
            number_fellow + 
            number_stuff
            )

        s.number = number
        s.price = price

        # Don't write to the database unless there is at least one sale
        if number != 0:
            s.save()

            if request.POST.get('unique_ticket') != 'None':
                T = models.Ticket.objects.get(unique_code=request.POST.get('unique_ticket'))
                T.collected = True
                T.save()

        if occ_id > '0':
            # How many tickets have been sold so far
            report['sold'] = occ_fin.total_tickets_sold()
            # Total number of tickets reserved
            report['how_many_reserved'] = occ_fin.tickets_sold()
            # How many tickets have been collected
            report['how_many_collected'] = occ_fin.tickets_sold() - models.Ticket.objects.get_collected(occurrence=occ_fin)
            # How many un-reserved tickets are there left to sell
            report['how_many_sales_left'] = occ_fin.maximum_sell - occ_fin.tickets_sold() - models.Sale.objects.sold_not_reserved(occurrence=occ_fin)
            # Maximum amount of free tickets to sell
            report['how_many_left'] = occ_fin.maximum_sell - occ_fin.tickets_sold()

            report['sale_percentage'] = (report['sold'] / float(occ_fin.maximum_sell)) * 100
            report['total_sales'] = occ_fin.total_sales()
            report['how_many_reserved'] = occ_fin.tickets_sold()
            report['reserve_percentage'] = (report['how_many_reserved'] / float(occ_fin.maximum_sell)) * 100
            report['max'] = occ_fin.maximum_sell

        context = {
            'report': report,
        }

        return render_to_response(
        'sale_overview_full.html',
        context,
        context_instance=RequestContext(request)
        )
    else:
        return HttpResponse(json.dumps('error'), content_type='application/json')


@login_required
def ReserveInputAJAX(request, show_name, occ_id):
    report = dict()

    if request.method == 'POST' and request.is_ajax():
        if occ_id > 0:
            unique_code = request.POST.get('unique_code')
            # runique_code = unique_code

            try:
                ticket = models.Ticket.objects.get(unique_code=unique_code)
                reservation = ticket.person_name
            except Ticket.DoesNotExist:
                reservation = 'None'

        context = {
            'unique_code': unique_code,
            'reservation': reservation,
        }
        return HttpResponse(json.dumps(context), content_type='application/json')

    else:
        return HttpResponse(json.dumps('error'), content_type='application/json')


@login_required
def GenReportAJAX(request):
    if request.method == 'POST' and request.is_ajax():
        content = ''
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        name = request.POST.get('name')
        label = request.POST.get('label')
        path = request.POST.get('path')

        if label == 'bug':
            # bug
            content = make_github_issue(
                title=subject,
                body=message + '.' + '\n >' + name  + '\n \n' +\
                    '*This bug was submitted at:* ' +\
                    '<a target="_blank" href="http://' + settings.BASE_URL + path + '"">' + path + '</a>',
                labels=['bug', 'ticket-bot']
                )
        elif label == 'improvment':
            # improve
            content = make_github_issue(
                title=subject,
                body=message + '.' + '\n >' + name + '\n \n' +\
                    '*This improvment was suggested at:* ' +\
                    '<a target="_blank" href="http://' + settings.BASE_URL + path + '"">' + path + '</a>',
                labels=['enhancement', 'ticket-bot']
                )
        else:
            content = make_github_issue(
                title=subject,
                body=message + '.' + '\n >' + name + '\n \n' +\
                    '*This issue was submitted at:* ' +\
                    '<a target="_blank" href="http://' + settings.BASE_URL + path + '"">' + path + '</a>',
                labels=['ticket-bot']
                )

        return HttpResponse(json.dumps(content), content_type='application/json')

    else:
        return HttpResponse(json.dumps(content), content_type='application/json')


def make_github_issue(title, body=None, labels=None):
    git = dict()
    # Github repo to POST data to
    url = 'https://api.github.com/repos/%s/%s/issues' % (settings.REPO_OWNER, settings.REPO_NAME)

    # Create an authenticated session to create the issue
    session = requests.session(headers={'Authorization': 'token %s' % keys.TOKEN})

    # Create our issue
    issue = {'title': title,
             'body': body,
             'labels': labels}
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))

    # Handle returned data from the server
    if r.status_code == 201:
        git['content'] = json.loads(r.content)
        git['err'] = False
        return git
    else:
        git['content'] = json.loads(r.content)
        git['err'] = True
        return git


@login_required
def SaleReport(request):
    now = datetime.datetime.now()
    time_filter = now - datetime.timedelta(weeks=4)
    show_list = models.Show.objects.filter(start_date__gte=time_filter).order_by('start_date')

    paginator = Paginator(show_list, 5)
    page = request.GET.get('page')

    try:
        show = paginator.page(page)
    except PageNotAnInteger:
        show = paginator.page(1)
    except EmptyPage:
        show = paginator.page(paginator.num_pages)

    context = {
        'show': show,
    }

    return render_to_response(
        'sale_report.html',
        context,
        context_instance=RequestContext(request)
        )


@login_required
def SaleReportFull(request, show_name):
    report = dict()
    show = models.Show.objects.get(id=show_name)
    occurrence = models.Occurrence.objects.filter(show=show)
    report['sale'] = models.Sale.objects.filter(id__in=occurrence)

    report['default_time'] = config.DEFAULT_TIME.strftime('%-I:%M %p').lower()
    report['default_time_matinee'] = config.DEFAULT_TIME_MATINEE.strftime('%-I:%M %p').lower()

    category = show.category

    if category.id == 1:
        pricing = models.InHousePricing.objects.get(id=1)

    # Fringe Pricing
    elif category.id == 2:
        pricing = models.FringePricing.objects.get(id=1)

    # External Pricing
    elif category.id == 3:
        pricing = models.ExternalPricing.objects.get(show_id=show_name)

    elif category.id == 4:
        pricing = models.StuFFPricing.objects.get(show_id=show_name)

    # Ticket Prices
    try:
        report['concession_price'] = float(pricing.concession_price)
    except Exception:
        report['concession_price'] = float(0)

    try:
        report['member_price'] = float(pricing.member_price)
    except Exception:
        report['member_price'] = float(0)

    try:
        report['public_price'] = float(pricing.public_price)
    except Exception:
        report['public_price'] = float(0)

    try:
        report['fringe_price'] = float(pricing.fringe_price)
    except Exception:
        report['fringe_price'] = float(0)

    try:
        report['matinee_freshers_price'] = float(pricing.matinee_freshers_price)
    except Exception:
        report['matinee_freshers_price'] = float(0)

    try:
        report['matinee_freshers_nnt_price'] = float(pricing.matinee_freshers_nnt_price)
    except Exception:
        report['matinee_freshers_nnt_price'] = float(0)

    report['season_price'] = models.SeasonTicketPricing.objects.get(id=1).season_ticket_price

    try:
        report['stuff_price'] = float(pricing.stuff_price)
    except Exception:
        report['stuff_price'] = float(0)

    context = {
        'show': show,
        'pricing': pricing,
        'occurrence': occurrence,
        'report': report,
    }

    return render_to_response(
        'sale_report_full.html', 
        context, 
        context_instance=RequestContext(request)
        )


@login_required
def DownloadReport(request, show_name):
    response = HttpResponse(content_type='text/csv')
    occurrence = models.Occurrence.objects.filter(show_id=show_name)
    show = get_object_or_404(models.Show, id=show_name)
    response['Content-Disposition'] = 'attachment; filename=Show_Report.csv'

    category = show.category

    if category.id == 1:
        pricing = models.InHousePricing.objects.get(id=1)

    # Fringe Pricing
    elif category.id == 2:
        pricing = models.FringePricing.objects.get(id=1)

    # External Pricing
    elif category.id == 3:
        pricing = models.ExternalPricing.objects.get(show_id=show_name)

    elif category.id == 4:
        pricing = models.StuFFPricing.objects.get(show_id=show_name)

    try:
        concession_sale = float(pricing.concession_price)
    except Exception:
        concession_sale = float(0)

    try:
        member_sale = float(pricing.member_price)
    except Exception:
        member_sale = float(0)

    try:
        public_sale = float(pricing.public_price)
    except Exception:
        public_sale = float(0)

    season_sale = float(models.SeasonTicketPricing.objects.get(id=1).season_ticket_price)

    try:
        fringe_sale = float(pricing.fringe_price)
    except Exception:
        fringe_sale = float(0)

    try:
        matinee_fresher_sale = float(pricing.matinee_freshers_price)
    except Exception:
        matinee_fresher_sale = float(0)

    try:
        matinee_fresher_nnt_sale = float(pricing.matinee_freshers_nnt_price)
    except Exception:
        matinee_fresher_nnt_sale = float(0)

    try:
        stuff_sale = float(pricing.stuff_price)
    except Exception:
        stuff_sale = float(0)

    writer = csv.writer(response)
    writer.writerow([
        show.name, 
        'Total Sales: £' + str(show.show_sales()), 
        'Total Tickets Sold: ' + str(show.total_tickets_sold_show()), 
        'Total Tickets Reserved: ' + str(show.total_tickets_reserved()),
        'Out of a possible: ' + str(show.total_possible())
        ])
    writer.writerow([
        'Show Day', 
        'Show Time',
        'Member Tickets',
        'Concession Tickets',
        'Public Tickets',
        'Season Tickets',
        'Season Ticket Sales',
        'Fellow Tickets',
        'StuFF Tickets',
        ])

    for oc in occurrence:
        writer.writerow([
            oc.day_formatted(), 
            oc.time_formatted(), 
            oc.member_tally(), 
            oc.concession_tally(), 
            oc.public_tally(),
            oc.season_tally(),
            oc.season_sale_tally(),
            oc.fellow_tally(),
            oc.stuff_tally(),
            ])
        writer.writerow([
            oc.day_formatted(),
            'TOTALS:',
            oc.member_tally() * member_sale,
            oc.concession_tally() * concession_sale, 
            oc.public_tally() * public_sale,
            '-',
            oc.season_sale_tally() * season_sale,
            '-',
            oc.stuff_tally() * stuff_sale,
            ])

    return response


def defaultFNI(request):
    html = "<html><body><h1>nt_tickets</h1><p>Function not implemented.</p></body></html>"
    return HttpResponse(html)


def book_landing(request, show_id):
    show = get_object_or_404(models.Show, id=show_id)
    if show.is_current() is False:
        return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}))
    step = 1
    total = 2
    message = "Tickets for performances are reserved online and payed for on collection at the box office."
    foh_contact = 'foh@newtheatre.org.uk'

    if request.method == 'POST':    # If the form has been submitted...
        form = forms.BookingFormLanding(request.POST, show=show)    # A form bound to the POST data
        if form.is_valid():     # All validation rules pass
            t = models.Ticket()
            person_name = form.cleaned_data['person_name']
            email_address = form.cleaned_data['email_address']

            t.person_name = person_name
            t.email_address = email_address
            # t.show = show
            occ_id = form.cleaned_data['occurrence']
            occurrence = models.Occurrence.objects.get(pk=occ_id)
            t.occurrence = occurrence
            if t.occurrence.date < datetime.date.today():
                return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}))
            t.quantity = form.cleaned_data['quantity']
            if t.occurrence.maximum_sell < (t.occurrence.tickets_sold()+t.quantity):
                return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}) + "?err=sold_out")

            try:
                tick = models.Ticket.objects.filter(
                    person_name = person_name,
                    email_address = email_address,
                    occurrence = occurrence
                    )

                tick_ordered = tick.order_by('-stamp')[0]
                if tick_ordered.stamp > datetime.datetime.now() - datetime.timedelta(0, 5, 0):
                    return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}) + "?err=time")
                else:
                    t.save()
            except IndexError:
                t.save()

            request.session["ticket"] = t

            email_html = get_template('email/confirm_inline.html').render(
                Context({
                    'show': show,
                    'ticket': t,
                    'settings': settings,
                    'customise': config,
                }))
            email_subject = 'Tickets reserved for ' + show.name
            email = EmailMessage(
                subject=email_subject,
                body=email_html,
                to=[t.email_address],
                from_email="boxoffice@newtheatre.org.uk"
                )
            email.content_subtype = 'html'

            if settings.ACTUALLY_SEND_MAIL == True:
                email.send()

            return HttpResponseRedirect(reverse('finish', kwargs={'show_id': show.id}))   # Redirect after POST
    else:
        form = forms.BookingFormLanding(show=show)    # An unbound form

    return render(request, 'book_landing.html', {
        'form': form,
        'show': show,
        'step': step,
        'total': total,
        'message': message,
        'foh_contact': foh_contact,
    })


@login_required
@cache_page(60 * 30)
def graph_view(request):
    all_shows = models.Show.objects.all().order_by('start_date')

    shows_date = []
    tickets_sold = []
    profit = []
    reserved_per_show = []

    most_popular = dict()
    least_popular = dict()

    most_popular['number'] = 0
    least_popular['number'] = 0

    category_tally = dict()

    category_tally['in_house'] = all_shows.filter(category=1).count()
    category_tally['fringe'] = all_shows.filter(category=2).count()
    category_tally['external'] = all_shows.filter(category=3).count()
    category_tally['stuff'] = all_shows.filter(category=4).count()
    category_tally['stuff_events'] = all_shows.filter(category=5).count()

    days = dict()
    days['tally'] = [0, 0, 0, 0, 0, 0, 0, 0]
    days['days'] = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Saturday Matinee']

    for i in range(1, 7):
        for oc in models.Occurrence.objects.all().filter(date__week_day=i):
            days['tally'][i-1] += oc.tickets_sold()

    for oc in models.Occurrence.objects.all().filter(date__week_day=7).filter(time__hour__gte=16):
            days['tally'][6] += oc.tickets_sold()

    for oc in models.Occurrence.objects.all().filter(date__week_day=7).filter(time__hour__gte=14).filter(time__hour__lt=16):
            days['tally'][7] += oc.tickets_sold()

    day_max = max(xrange(len(days['tally'])),key=days['tally'].__getitem__)
    day_min = min(xrange(len(days['tally'])),key=days['tally'].__getitem__)

    days['max'] = [days['tally'][day_max], days['days'][day_max]]
    days['min'] = [days['tally'][day_min], days['days'][day_min]]

    for sh in all_shows:
        if sh.total_tickets_reserved() > most_popular['number']:
            most_popular['number'] = sh.total_tickets_reserved()
            most_popular['show'] = sh.name
            most_popular['date'] = sh.date_formatted()

    least_popular['number'] = most_popular['number']

    for sh in all_shows:
        if sh.total_tickets_reserved() < least_popular['number'] and sh.total_tickets_reserved() != 0:
            least_popular['number'] = sh.total_tickets_reserved()
            least_popular['show'] = sh.name
            least_popular['date'] = sh.date_formatted()

    for i in range(1, 13):
        queryset = all_shows.filter(start_date__month=i)
        sold = 0
        show_profit = 0
        for sh in queryset:
            sold += sh.total_tickets_reserved()
            show_profit += sh.show_sales()

        tickets_sold.append(sold)
        profit.append(show_profit)

        shows_date.append(queryset.count())
        try:
            reserve_maths = sold / queryset.count()
        except:
            reserve_maths = 0

        reserved_per_show.append(reserve_maths)

    months = json.dumps(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])

    shows_by_month = json.dumps({
        'label': "Shows by month",
        'fillColor': "rgba(255, 196, 37, 0.2)",
        'strokeColor': "rgba(255, 196, 37, 1)",
        'pointColor': "rgba(255, 196, 37, 1)",
        'pointStrokeColor': "#fff",
        'pointHighlightFill': "#fff",
        'pointHighlightStroke': "rgba(255, 196, 37, 1)",
        'data': shows_date
    })

    tickets_sold = json.dumps({
        'label': "Tickets sold",
        'fillColor': "rgba(226, 0, 19, 0.2)",
        'strokeColor': "rgba(226, 0, 19, 1)",
        'pointColor': "rgba(226, 0, 19, 1)",
        'pointStrokeColor': "#fff",
        'pointHighlightFill': "#fff",
        'pointHighlightStroke': "rgba(226, 0, 19, 1)",
        'data': tickets_sold
        })

    profit = json.dumps({
        'label': "Show Profit",
        'fillColor': "rgba(60, 216, 97, 0.2)",
        'strokeColor': "rgba(60, 216, 97, 1)",
        'pointColor': "rgba(60, 216, 97, 1)",
        'pointStrokeColor': "#fff",
        'pointHighlightFill': "#fff",
        'pointHighlightStroke': "rgba(60, 216, 97, 1)",
        'data': profit
        })

    reserved_by_show = json.dumps({
        'label': "Shows by month",
        'fillColor': "rgba(74, 174, 219, 0.2)",
        'strokeColor': "rgba(74, 174, 219, 1)",
        'pointColor': "rgba(74, 174, 219, 1)",
        'pointStrokeColor': "#fff",
        'pointHighlightFill': "#fff",
        'pointHighlightStroke': "rgba(74, 174, 219, 1)",
        'data': reserved_per_show
    })


    context = {
        'months': months,
        'shows_by_month': shows_by_month,
        'tickets_sold': tickets_sold,
        'reserved_by_show': reserved_by_show,
        'category_tally': category_tally,
        'days': days,
        'profit': profit,
        'most_popular': most_popular,
        'least_popular': least_popular,
        }

    return render_to_response(
        'graph_view.html', 
        context, 
        context_instance=RequestContext(request)
        )


def how_many_left(request):
    if 'occ' in request.GET:
        occ = get_object_or_404(models.Occurrence, pk=request.GET['occ'])

        response_data = {}
        response_data['sold_out'] = occ.sold_out()
        left = occ.maximum_sell - occ.tickets_sold()
        if left <= settings.MAX_DISCLOSURE:
            response_data['more_than_max'] = False
            response_data['how_many_left'] = left
        else:
            response_data['more_than_max'] = True
            response_data['how_many_left'] = settings.MAX_DISCLOSURE
        response_data['error'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        response_data = {}
        response_data['error'] = True
        response_data['error_message'] = 'Required parameters not given'
        return HttpResponse(json.dumps(response_data), content_type="application/json")


def book_finish(request, show_id):
    show = models.Show.objects.get(id=show_id)
    ticket = request.session["ticket"]

    return render(request, 'book_finish.html', {
        'show': show,
        'ticket': ticket,
    })


def book_error(request, show_id):
    if 'err' in request.GET:
        err = request.GET['err']
    else:
        err = None
    return render(request, 'book_error.html', {'err': err})


def list(request):
    shows = models.Show.objects.all()

    return render(request, 'list.html', {
        'shows': shows
    })


class OrderedListView(ListView):

    def get_queryset(self):
        return super(OrderedListView, self).get_queryset().order_by(self.order_by)


class ListShows(OrderedListView):
    model = models.Show
    template_name = 'list_shows.html'
    context_object_name = 'shows'
    order_by = 'start_date'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ListShows, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context

    def get_queryset(self):
        today = datetime.date.today()
        return super(ListShows, self).get_queryset().filter(end_date__gte=today)
        #.filter(category__slug__in=settings.PUBLIC_CATEGORIES)


class ListPastShows(OrderedListView):
    model = models.Show
    template_name = 'list_past_shows.html'
    context_object_name = 'shows'
    order_by = '-start_date'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ListPastShows, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context

    def get_queryset(self):
        today = datetime.date.today()
        return super(ListPastShows, self).get_queryset().filter(end_date__lte=today)


class DetailShow(DetailView):
    model = models.Show
    template_name = 'detail_show.html'
    context_object_name = 'show'


def sidebar(request):
    categories = models.Category.objects.all().exclude(sort=0).order_by('sort')
    today = datetime.date.today()
    limit = today + datetime.timedelta(weeks=config.SIDEBAR_FILTER_PERIOD)
    exclude = config.SIDEBAR_FILTER_PERIOD
    current_shows = []
    for category in categories:
        shows = models.Show.objects.filter(category=category).filter(end_date__gte=today).order_by('end_date').filter(start_date__lte=limit).filter(category__slug__in=config.PUBLIC_CATEGORIES)
        if len(shows) > 0:
            current_shows.append(shows[0])
    return render(request, 'sidebar.html', {'shows': current_shows, 'exclude': exclude, 'settings': settings})


def cancel(request, ref_id):
    ticket = get_object_or_404(models.Ticket, unique_code=ref_id)
    if request.POST.get("id", "") == ticket.unique_code:
        ticket.cancelled = True
        ticket.save()
        cancelled = True
        already_cancelled = False
    elif ticket.cancelled is True:
        already_cancelled = True
        cancelled = False
    else:
        cancelled = False
        already_cancelled = False

    context = {
        'ticket': ticket,
        'cancelled': cancelled,
        'already_cancelled': already_cancelled,
    }

    return render(request, 'cancel.html', context)
