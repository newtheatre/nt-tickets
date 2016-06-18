from django import template
from tickets import models
# Register for inclusion tag
register = template.Library()

# Sale overview element on show report page
@register.inclusion_tag('sale_overview.html')
def ShowSaleOverview(report):
    report = report

    context = {
        'report': report,
    }
    return context

# Occurrence profit
@register.inclusion_tag('sale_final.html')
def ShowSales(report):
  report = report

  context = {
    'report': report
  }
  return context

# Reservation modal
@register.inclusion_tag('reservation_modal.html')
def ReservationModal(occurrence=None, have_form=False, occ_id=None):
  if occ_id:
    tickets = models.Occurrence.objects.get(pk=occ_id).ticket_set.all()
  else:
    tickets = models.Occurrence.objects.get(pk=occurrence[0]).ticket_set.all()

  context = {
    'have_form': have_form,
    'tickets': tickets,
  }
  return context
  
@register.filter
def mul(value, arg):
  """Multiply the arg with the value."""
  try:
      return format((value * arg), '.2f')
  except Exception:
      return ''