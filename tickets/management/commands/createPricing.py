from django.core.management.base import BaseCommand
import configuration.customise as config
from pricing import models


class Command(BaseCommand):
    help = 'Creates default pricing objects when creating a new database'

    def handle(self, *args, **options):

        if not models.SeasonTicketPricing.objects.all().exists():
            models.SeasonTicketPricing.objects.create(
                season_sale_price='40.00',
                season_sale_nnt_price='20.00'
            )

        if not models.InHousePricing.objects.all().exists():
            models.InHousePricing.objects.create(
                concession_price='5.00',
                public_price='8.00',
                member_price='5.00',
                matinee_freshers_price='2.50',
                matinee_freshers_nnt_price='2.00'
            )

        if not models.FringePricing.objects.all().exists():
            models.FringePricing.objects.create(
                fringe_price='3.00'
            )

        if not models.StuFFPassPricing.objects.all().exists():
            models.StuFFPassPricing.objects.create(
                festival_pass=config.FESTIVAL_SALES_PRICE[0],
                day_pass=config.DAY_SALES_PRICE[0],
                performer_pass=config.PERFORMER_SALES_PRICE[0],
            )
