from django import template
# Register for inclusion tag
register = template.Library()


# Sale overview element on show report page
@register.inclusion_tag('sale_overview.html')
def ShowSaleOverview(price):
    report = price

    context = {
        'report': report
    }
    return context