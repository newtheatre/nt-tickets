from django.contrib import admin
from django.template import RequestContext
from django.conf.urls.defaults import patterns
from django.shortcuts import render_to_response

from tickets.models import *
from tickets.forms import ReportForm

class TicketAdmin(admin.ModelAdmin):
    review_template = 'report.html'
 
    def get_urls(self):
        urls = super(TicketAdmin, self).get_urls()
        my_urls = patterns('',
            (r'$',self.admin_site.admin_view(self.report_index)),
            (r'\d+/report/$', self.admin_site.admin_view(self.review)),
        )
        return my_urls + urls

    def report_index(self,request):
        report=dict()
        report['have_report']=False
        occurrence=""

        if request.method=='POST':
            form = ReportForm(request.POST)
            if form.is_valid():
                occurrence=form.cleaned_data['occurrence']
                report['tickets']=Ticket.objects.filter(occurrence=occurrence).order_by('person_name')
                report['how_many_sold']=occurrence.tickets_sold()
                report['how_many_left']=occurrence.maximum_sell-occurrence.tickets_sold()
                report['percentage']=(report['how_many_sold']/float(occurrence.maximum_sell))*100
                report['have_report']=True
            else:
                pass        
        else:
            form=ReportForm()

        return render_to_response('admin/tickets_index.html', {
            'form':form,
            'occurrence':occurrence,
            'report':report,
        }, context_instance=RequestContext(request))
 
    def review(self, request, id=5):
        entry = Ticket.objects.get(pk=id)
 
        return render_to_response('self.review_template', {
            
        }, context_instance=RequestContext(request))


admin.site.register(Show)
admin.site.register(Category)
admin.site.register(Occurrence)
admin.site.register(Ticket,TicketAdmin)