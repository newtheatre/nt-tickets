from django.contrib import admin
from django.template import RequestContext
from django.conf.urls import url
from django.shortcuts import render
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.forms import CheckboxSelectMultiple
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
                report['tickets'] = Ticket.objects.filter(
                    occurrence=occurrence).order_by('person_name')
                report['how_many_sold'] = occurrence.tickets_sold()
                report['how_many_left'] = occurrence.maximum_sell - \
                    occurrence.tickets_sold()
                report['percentage'] = (report['how_many_sold'] /
                                        float(occurrence.maximum_sell)) * 100
                report['have_report'] = True
            elif C_form.is_valid():
                ticket_id = C_form.cleaned_data['ticket']
                occurrence_id = C_form.cleaned_data['occurrence']

                ticket = Ticket.objects.get(unique_code=ticket_id)

                ticket.cancelled = True
                ticket.save()

                occurrence = Occurrence.objects.get(unique_code=occurrence_id)

                report['tickets'] = Ticket.objects.filter(
                    occurrence=occurrence).order_by('person_name')
                report['how_many_sold'] = occurrence.tickets_sold()
                report['how_many_left'] = occurrence.maximum_sell - \
                    occurrence.tickets_sold()
                report['percentage'] = (report['how_many_sold'] /
                                        float(occurrence.maximum_sell)) * 100
                report['have_report'] = True

                R_form = ReportForm(initial={'occurrence': occurrence})
            elif D_form.is_valid():
                occurrence_id = D_form.cleaned_data['occurrence']
                occurrence = Occurrence.objects.get(unique_code=occurrence_id)
                tickets = Ticket.objects.filter(
                    occurrence=occurrence).order_by('person_name')

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

                report['tickets'] = Ticket.objects.filter(
                    occurrence=occurrence).order_by('person_name')
                report['how_many_sold'] = occurrence.tickets_sold()
                report['how_many_left'] = occurrence.maximum_sell - \
                    occurrence.tickets_sold()
                report['percentage'] = (report['how_many_sold'] /
                                        float(occurrence.maximum_sell)) * 100
                report['have_report'] = True

                R_form = ReportForm(initial={'occurrence': occurrence})

                return response
            else:
                pass

        else:
            R_form = ReportForm()
            C_form = CancelForm()
            D_form = DownloadForm()

        context = {
            'R_form': R_form,
            'C_form': C_form,
            'D_form': D_form,
            'occurrence': occurrence,
            'report': report,
        }
        
        return render(request, 'admin/tickets_index.html', context)

    def review(self, request, id=5):
        entry = Ticket.objects.get(pk=id)

        return render(request, 'self.review_template', {})

class OccurrenceInline(admin.TabularInline):
    model = Occurrence
    min_num = 0
    extra = 1

    fieldsets = (
        (None, {
            'fields':(
                'date',
                'time',
                'maximum_sell',
                'hours_til_close',
                ),
            }),
        )

class ExternalPriceInline(admin.TabularInline):
    model = pricing.ExternalPricing
    max_num = 1
    min_num = 1

    fieldsets = (
        (None, {
            'fields':(
                'concession_price',
                'member_price',
                'public_price',
                'allow_season_tickets',
                'allow_fellow_tickets',
                'allow_half_matinee',
                'allow_half_nnt_matinee',
                ),
            }),
        )

    # Disable delete button
    def has_delete_permission(self, request, obj=None):
        return False

class StuFFPriceInline(admin.TabularInline):
    model = pricing.StuFFPricing
    max_num = 1
    min_num = 1

    fieldsets = (
        (None, {
            'fields':('stuff_price',)
            }),
        )

    # Disable delete button
    def has_delete_permission(self, request, obj=None):
        return False

class StuFFEventPriceInline(admin.TabularInline):
    model = pricing.StuFFEventPricing
    max_num = 1
    min_num = 1

    fieldsets = (
        (None, {
            'fields':('show', 'concession_price', 'public_price', 'member_price',),
            }),
        )


def get_emails(modeladmin, request, queryset):
    get_emails.short_description = "Get Emails"
    data = dict()
    for show in queryset:
        occurrences = Occurrence.objects.all().filter(show=show)
        for occ in occurrences:
            data[occ.__str__()] = dict()
            tickets = Ticket.objects.all().filter(occurrence=occ, cancelled=False, collected=False)
            for tick in tickets:
                data[occ.__str__()][tick.person_name] = tick.email_address

    context = {
        'data': data,
        'title': 'Email list for selected shows'
    }

    return TemplateResponse(request, 'admin/get_emails.html', context)


class ShowAdmin(admin.ModelAdmin):
    actions = [get_emails]
    fieldsets = (
        (None, {
            'fields':(
                'name',
                'location',
                'category',
                ('runtime', 'interval_number'),
                'poster',
                'description',
                'long_description',
                ('start_date',
                'end_date'),
                ),
            'description': 'Press \'Save and continue editing\' to display pricing for StuFF and External shows.'
            }),
        ('Advanced Options', {
            'fields': ('slug',),
            'classes': ('collapse',),
          }),
        ('Content Warnings', {
            'fields': ('warnings_technical', 'warnings_action', 'warnings_dialogue', 'warnings_notes'),
            'classes': ('collapse',),
        }),
        )
    inlines = [
        OccurrenceInline,
    ]

    filter_horizontal = ('warnings_dialogue', 'warnings_action', 'warnings_technical')

    list_display = (
        'pk',
        'name',
        'location',
        'category',
        'start_date',
        'end_date',
        'num_occurrences',
        )

    list_filter = ['category']
    search_fields = ('name', 'description')

    def get_actions(self, request):
        actions = super(ShowAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'get_emails' in actions:
                del actions['get_emails']

        return actions

    def num_occurrences(self, obj):
        return obj.occurrence_set.count()
    num_occurrences.short_description = 'Occurrences'

    # Only retrieve recent shows to edit
    def get_queryset(self, request):
        # time_filter = datetime.datetime.now() - datetime.timedelta(weeks=4)
        return Show.objects.order_by('-start_date')

    # Get pricing admin options on form save
    def change_view(self, request, object_id, form_url='', extra_context=None):
        cat = Show.objects.get(pk=object_id).category.name
        current_inlines = []

        if cat == 'External':
            current_inlines = [OccurrenceInline, ExternalPriceInline,]
        elif cat == 'StuFF':
            current_inlines = [OccurrenceInline, StuFFPriceInline,]
        elif cat == 'StuFF Events':
            current_inlines = [OccurrenceInline, StuFFEventPriceInline,]
        else:
            current_inlines = [OccurrenceInline,]

        # CODE TO FILL INLINES BASED ON PRODUCT
        self.inlines = current_inlines
        return super(ShowAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

class ContentWarningAdmin(admin.ModelAdmin):
    ordering = ['category', 'title']
    list_display = ('title', 'category')
    search_fields = ['title']
    list_filter = ['category']

    def make_tech(modeladmin, request, queryset):
        queryset.update(category='1')
    def make_content(modeladmin, request, queryset):
        queryset.update(category='2')

    actions = [make_tech, make_content]

class SaleAdmin(admin.ModelAdmin):
    ordering = ['stamp']
    # Disable editing of values, delete only.
    readonly_fields=(
        'ticket',
        'occurrence',
        'price', 
        'stamp')
    fields = [
        readonly_fields
    ]

    list_display = ('occurrence', 'ticket', 'price', 'stamp')
    search_fields = ['occurrence']
    list_filter = ['occurrence']


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
    search_fields = ['show__name']

    def get_queryset(self, request):
        time_filter = datetime.datetime.now() - datetime.timedelta(weeks=1)
        return Occurrence.objects.filter(date__gte=time_filter).order_by('date', 'time')

    def get_form(self, request, obj=None, **kwargs):
        time_filter = datetime.datetime.now() - datetime.timedelta(weeks=1)
        form = super(OccurrenceAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['show'].queryset = Show.objects.filter(
            start_date__gte=time_filter).order_by('start_date')
        return form


class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'slug', 'sort']
    list_display = ('name', 'slug', 'sort')
    ordering = ['sort']
    search_fields = ['show']

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False


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
    fields = ['season_sale_price', 'season_sale_nnt_price']

    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


class StuFFPriceAdmin(admin.ModelAdmin):
    fields = ['show', 'stuff_price', ]


class StuFFEventPriceAdmin(admin.ModelAdmin):
    fields = ['show', 'concession_price', 'public_price', 'member_price']

class StuFFPassAdmin(admin.ModelAdmin):
    fields = ['day_pass', 'festival_pass']

# admin.site.unregister(Site)
admin.site.register(Show, ShowAdmin)
admin.site.register(Category, CategoryAdmin)
# admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(ContentWarning, ContentWarningAdmin)
admin.site.register(pricing.InHousePricing, InHousePriceAdmin)
admin.site.register(pricing.ExternalPricing, ExternalPriceAdmin)
admin.site.register(pricing.SeasonTicketPricing, SeasonPriceAdmin)
admin.site.register(pricing.FringePricing, FringePriceAdmin)
admin.site.register(pricing.StuFFPricing, StuFFPriceAdmin)
admin.site.register(pricing.StuFFEventPricing, StuFFEventPriceAdmin)
admin.site.register(pricing.StuFFPassPricing, StuFFPassAdmin)
