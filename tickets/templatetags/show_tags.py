from django import template
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
def ReservationModal(report):
  report = report

  context = {
    'report': report
  }
  return context
  