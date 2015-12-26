from django.contrib import admin
from django.template import RequestContext
from django.conf.urls import url
from django.shortcuts import render_to_response

from tickets.models import *
from tickets.forms import ReportForm, CancelForm


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
            R_form = ReportForm(request.POST)
            C_form = CancelForm(request.POST)
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
            else:
                pass

        else:
            R_form = ReportForm()
            C_form = CancelForm()

        return render_to_response('admin/tickets_index.html', {
            'R_form': R_form,
            'C_form': C_form,
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
    ordering = ['start_date', 'name']
    search_fields = ('name', 'description')


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

    ordering = ['date', 'time']
    search_fields = ['show']


class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'slug', 'sort',]
    list_display = ('name', 'slug', 'sort',)
    ordering = ['sort']
    search_fields = ['show']

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

    list_display = [
        'show', 
        'concession_price',
        'member_price',
        'public_price',
        'allow_season_tickets',
        'allow_fellow_tickets',
        'allow_half_matinee',
        'allow_half_nnt_matinee'
        ]

    search_fields = ['show']

admin.site.register(Show, ShowAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(ExternalPricing, ExternalPriceAdmin)
