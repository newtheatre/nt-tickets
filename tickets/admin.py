from django.contrib import admin
from django.template import RequestContext
from django.conf.urls import url
from django.shortcuts import render_to_response
from django.contrib.sites.models import Site
from django.http import HttpResponse
import csv

from datetime import datetime

from tickets.models import *
import pricing.models as pricing
from tickets.forms import ReportForm, CancelForm, DownloadForm


class TicketAdmin(admin.ModelAdmin):
    review_template = 'report.html'

    def get_urls(self):
        urls = super(TicketAdmin, self).get_urls()
        my_urls = [
            url(r'$', self.admin_site.admin_view(self.report_index)),
            url(r'\d+/report/$', self.admin_site.admin_view(self.review)),
        ]
        return my_urls + urls

    def report_index(self, request):
        report = dict()
        report['have_report'] = False
        occurrence = ""

        if request.method == 'POST':
            R_form = ReportForm(request.POST)       # Report Form
            C_form = CancelForm(request.POST)       # Cancellation Form
            D_form = DownloadForm(request.POST)     # Download Form
            if R_form.is_valid():
                occurrence = R_form.cleaned_data['occurrence']
                report['tickets'] = Ticket.objects.filter(occurrence=occurrence).order_by('person_name')
                report['how_many_sold'] = occurrence.tickets_sold()
                report['how_many_left'] = occurrence.maximum_sell-occurrence.tickets_sold()
                report['percentage'] = (report['how_many_sold']/float(occurrence.maximum_sell))*100
                report['have_report'] = True
            elif C_form.is_valid():
                ticket_id = C_form.cleaned_data['ticket']
                occurrence_id = C_form.cleaned_data['occurrence']

                ticket = Ticket.objects.get(unique_code=ticket_id)

                ticket.cancelled = True
                ticket.save()

                occurrence = Occurrence.objects.get(unique_code=occurrence_id)

                report['tickets'] = Ticket.objects.filter(occurrence=occurrence).order_by('person_name')
                report['how_many_sold'] = occurrence.tickets_sold()
                report['how_many_left'] = occurrence.maximum_sell-occurrence.tickets_sold()
                report['percentage'] = (report['how_many_sold']/float(occurrence.maximum_sell))*100
                report['have_report'] = True

                R_form = ReportForm(initial={'occurrence': occurrence})
            elif D_form.is_valid():
                occurrence_id = D_form.cleaned_data['occurrence']
                occurrence = Occurrence.objects.get(unique_code=occurrence_id)
                tickets = Ticket.objects.filter(occurrence=occurrence).order_by('person_name')

                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=Reservation_Report.csv'

                writer = csv.writer(response)

                writer.writerow([
                    occurrence.show.name,
                    occurrence.day_formatted(),
                    occurrence.time_formatted(),
                    'Total Reserved: ' + str(occurrence.tickets_sold()),
                    'Out of: ' + str(occurrence.maximum_sell)
                    ])

                writer.writerow([
                    'Person Name',
                    'Quantity Reserved',
                    'TimeStamp',
                    'Cancelled?',
                    'Collected?'
                    ])

                for tick in tickets:
                    writer.writerow([
                        tick.person_name,
                        tick.quantity,
                        tick.stamp,
                        tick.cancelled,
                        tick.collected
                        ])


                report['tickets'] = Ticket.objects.filter(occurrence=occurrence).order_by('person_name')
                report['how_many_sold'] = occurrence.tickets_sold()
                report['how_many_left'] = occurrence.maximum_sell-occurrence.tickets_sold()
                report['percentage'] = (report['how_many_sold']/float(occurrence.maximum_sell))*100
                report['have_report'] = True

                R_form = ReportForm(initial={'occurrence': occurrence})
                
                return response
            else:
                pass

        else:
            R_form = ReportForm()
            C_form = CancelForm()
            D_form = DownloadForm()

        return render_to_response('admin/tickets_index.html', {
            'R_form': R_form,
            'C_form': C_form,
            'D_form': D_form,
            'occurrence': occurrence,
            'report': report,
        }, context_instance=RequestContext(request))

    def review(self, request, id=5):
        entry = Ticket.objects.get(pk=id)

        return render_to_response('self.review_template', {

        }, context_instance=RequestContext(request))


class ShowAdmin(admin.ModelAdmin):
    fields = [
            'name',
            'location',
            'category',
            'poster',
            'slug',
            'description',
            'long_description',
            'start_date',
            'end_date'
            ]

    list_display = (
                'name',
                'location',
                'category',
                'start_date',
                'end_date')

    list_filter = ['category']
    search_fields = ('name', 'description')

    def get_queryset(self, request):
        time_filter = datetime.datetime.now() - datetime.timedelta(weeks=1)
        return Show.objects.filter(start_date__gte=time_filter).order_by('start_date')


class OccurrenceAdmin(admin.ModelAdmin):
    fields = [
            'show',
            'date',
            'time',
            'maximum_sell',
            'hours_til_close'
            ]

    list_display = (
                'show',
                'date',
                'time',
                'maximum_sell',
                'hours_til_close'
                )

    search_fields = ['show']

    

    def get_queryset(self, request):
        time_filter = datetime.datetime.now() - datetime.timedelta(weeks=1)
        return Occurrence.objects.filter(date__gte=time_filter).order_by('date', 'time')

    def get_form(self, request, obj=None, **kwargs):
        time_filter = datetime.datetime.now() - datetime.timedelta(weeks=1)
        form = super(OccurrenceAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['show'].queryset = Show.objects.filter(start_date__gte=time_filter).order_by('start_date')
        return form


class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'slug', 'sort']
    list_display = ('name', 'slug', 'sort')
    ordering = ['sort']
    search_fields = ['show']


class InHousePriceAdmin(admin.ModelAdmin):
    fields = [
        'concession_price',
        'member_price',
        'public_price',
        'matinee_freshers_price',
        'matinee_freshers_nnt_price'
    ]

    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
          return False
        else:
          return True

    def has_delete_permission(self, request, obj=None):
        return False


class FringePriceAdmin(admin.ModelAdmin):
    fields = [
        'fringe_price'
    ]

    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
          return False
        else:
          return True

    def has_delete_permission(self, request, obj=None):
        return False


class ExternalPriceAdmin(admin.ModelAdmin):
    fields = [
        'show',
        'concession_price',
        'member_price',
        'public_price',
        'allow_season_tickets',
        'allow_fellow_tickets',
        'allow_half_matinee',
        'allow_half_nnt_matinee'
        ]


class SeasonPriceAdmin(admin.ModelAdmin):
    fields = ['season_ticket_price']

    list_display = ['season_ticket_price']

    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
          return False
        else:
          return True

    def has_delete_permission(self, request, obj=None):
        return False


class StuFFPriceAdmin(admin.ModelAdmin):
    fields = ['show', 'ticket_price',]


class StuFFEventPriceAdmin(admin.ModelAdmin):
    fields = ['show', 'concession_price', 'public_price', 'member_price']


# admin.site.unregister(Site)
admin.site.register(Show, ShowAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(pricing.InHousePricing, InHousePriceAdmin)
admin.site.register(pricing.ExternalPricing, ExternalPriceAdmin)
admin.site.register(pricing.SeasonTicketPricing, SeasonPriceAdmin)
admin.site.register(pricing.FringePricing, FringePriceAdmin)
admin.site.register(pricing.StuFFPricing, StuFFPriceAdmin)
admin.site.register(pricing.StuFFEventPricing, StuFFEventPriceAdmin)

