from django.test import TestCase
from models import *

from datetime import date, timedelta, datetime


class TestPricing(TestCase):

    @classmethod
    def setUpTestData(cls):
        today = date.today()
        cat = Category.objects.create(name='Test Category', slug='test', sort=1)

        cls.show1 = Show.objects.create(name='S1', category=cat, description='huh',
                                        long_description='ooh', start_date=today, end_date=today + timedelta(days=2))

        cls.season = SeasonTicketPricing.objects.create(season_ticket_price=40)
        cls.in_house = InHousePricing.objects.create(
            matinee_freshers_price=4, matinee_freshers_nnt_price=5)
        cls.fringe = FringePricing.objects.create(fringe_price=2)
        cls.external = ExternalPricing.objects.create(show=cls.show1)
        cls.stuff = StuFFPricing.objects.create(show=cls.show1)
        cls.stuff_events = StuFFEventPricing.objects.create(show=cls.show1)

    def test_season_prices(self):
        season = self.season

        name = season.__str__()
        p = season.season_ticket_price

        self.assertEqual(name, 'Season Ticket Pricing')
        self.assertEqual(p, 40)

    def test_in_house_prices(self):
        in_house = self.in_house

        name = in_house.__str__()
        p1 = in_house.matinee_freshers_price
        p2 = in_house.matinee_freshers_nnt_price

        self.assertEqual(name, 'In House Pricing')
        self.assertEqual(p1, 4)
        self.assertEqual(p2, 5)

    def test_fringe_prices(self):
        fringe = self.fringe

        name = fringe.__str__()
        p = fringe.fringe_price

        self.assertEqual(name, 'Fringe Pricing')
        self.assertEqual(p, 2)

    def test_external_prices(self):
        external = self.external

        name = external.__str__()
        S = ('Pricing for: ' + self.show1.name)

        self.assertEqual(name, S)

    def test_stuff_prices(self):
        stuff = self.stuff

        name = stuff.__str__()
        S = ('Pricing for: ' + self.show1.name)

        self.assertEqual(name, S)

    def test_stuff_events_prices(self):
        stuff_events = self.stuff_events

        name = stuff_events.__str__()
        S = ('Pricing for: ' + self.show1.name)

        self.assertEqual(name, S)
