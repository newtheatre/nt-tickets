from django.contrib import admin
from tickets.models import *

class TicketAdmin(admin.ModelAdmin):
    list_filter = ['occurrence']

admin.site.register(Show)
admin.site.register(Occurrence)
admin.site.register(Ticket,TicketAdmin)