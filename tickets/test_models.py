from django.test import TestCase
from django.core.files import File
from models import *
from markdown2 import Markdown
# from django_any import any_model

from datetime import date, timedelta, datetime
from django.utils import timezone


class StaticPageTest(TestCase):

    def test_list_view(self):
        response = self.client.get('/list/')
        self.assertEqual(response.status_code, 200)

    def test_sidebar_view(self):
        response = self.client.get('/sidebar/')
        self.assertEqual(response.status_code, 200)


class BookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name='Test Category', slug='test', sort=1)
        cls.start_date = date.today() + timedelta(days=2)
        cls.end_date = date.today() + timedelta(days=5)
        cls.show = {
        1: Show.objects.create(
            name='Test Show',
            location='Somewhere',
            description='Some Info',
            start_date=cls.start_date,
            end_date=cls.end_date,
            category=cls.cat
            )
        }

    def test_category_name(self):
        self.assertEqual(self.cat.__str__(), 'Test Category')

    def test_show_exists(self):
        self.assertEqual(self.show[1].name, 'Test Show')

    def test_book_form(self):
        response = self.client.get('/book/1/')
        self.assertEqual(response.status_code, 200)

    def test_show_sold_out_false(self):
        self.assertEqual(self.show[1].show_sold_out(), False)

    def test_has_occurrences_false(self):
        self.assertEqual(self.show[1].has_occurrences(), False)


class ShowTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name='Test Category', slug='test', sort=1)
        cls.today = date.today()
        cls.now = datetime.now()
        cls.desc = 'A show somewhere'
        cls.l_desc = 'A longer show somewhere'

        # Create some good shows
        cls.show = {
            1: Show.objects.create(name='S1', category=cls.cat, description='show current', long_description=cls.l_desc, start_date=cls.today, end_date=cls.today + timedelta(days=6)),
            2: Show.objects.create(name='S2', category=cls.cat, description='show past', long_description=cls.l_desc, start_date=cls.today - timedelta(days=6), end_date=cls.today - timedelta(days=1)),
            3: Show.objects.create(name='S3', category=cls.cat, description='show closed', long_description=cls.l_desc, start_date=cls.today, end_date=cls.today + timedelta(days=4)),
        }

        # Create an occurrence
        occ_day = datetime.now() + timedelta(hours=4)

        cls.occ = {
            1: Occurrence.objects.create(show=cls.show[1], date=occ_day.date(), time=occ_day.time(), maximum_sell=2, hours_til_close=0),
            2: Occurrence.objects.create(show=cls.show[2], date=occ_day.date(), time=occ_day.time(), maximum_sell=2, hours_til_close=0),
            3: Occurrence.objects.create(show=cls.show[3], date=datetime.now().date(), time=datetime.now().time(), maximum_sell=2, hours_til_close=2),
        }

        cls.ticket = {
            1: Ticket.objects.create(occurrence=cls.occ[1], person_name='testman', email_address='test@test.com', quantity=1),
            2: Ticket.objects.create(occurrence=cls.occ[2], person_name='testman2', email_address='test@test.com', quantity=2),
            3: Ticket.objects.create(occurrence=cls.occ[3], person_name='testman3', email_address='test@test.com', quantity=1),
        }
        

        cls.sale = Sale.objects.create(
            occurrence=cls.occ[1], ticket='None', price=1, number=2)

    def test_is_current_false(self):
        self.assertEqual(self.show[2].is_current(), False)

    def test_sold_out_true(self):
        self.assertTrue(self.show[2].show_sold_out())
        self.assertTrue(self.occ[2].sold_out())

    def test_sold_out_false(self):
        self.assertFalse(self.show[1].show_sold_out())
        self.assertFalse(self.occ[1].sold_out())

    def test_has_occurrences_true(self):
        self.assertTrue(self.show[1].has_occurrences())

    def test_show_name(self):
        self.assertEqual(self.show[1].__str__(), self.show[1].name)

    def test_markdown(self):
        ld_md = '<p>A longer show somewhere</p>\n'
        self.assertEqual(self.show[1].long_markdown(), ld_md)

    def test_datetime_formatted(self):
        occ = self.occ[1]
        day_format = occ.date.strftime('%A')
        time_format = occ.time.strftime('%-I:%M %p').lower()
        datetime_format = occ.date.strftime('%A %d %B ') + \
            occ.time.strftime('%-I:%M %p').lower()

        self.assertEqual(occ.day_formatted(), day_format)
        self.assertEqual(occ.time_formatted(), time_format)
        self.assertEqual(occ.datetime_formatted(), datetime_format)

    def test_occurrence_str(self):
        occ = self.occ[1]
        occ_str = occ.show.name + \
            " on " + str(occ.day_formatted()) + \
            " at " + str(occ.time_formatted())
        self.assertEqual(occ.__str__(), occ_str)

    def test_ticket_str(self):
        tick = self.ticket[1]
        tick_str = tick.occurrence.show.name + \
            " on " + str(tick.occurrence.date) + \
            " at " + str(tick.occurrence.time) + \
            " for " + tick.person_name

        self.assertEqual(tick.__str__(), tick_str)

    def test_get_available(self):
        occ = self.occ[1]
        datetime_format = occ.date.strftime('%A %d %B ') + \
            occ.time.strftime('%-I:%M %p').lower()

        r1 = Occurrence.objects.get_available(self.show[1])

        self.assertEqual(occ.sold_out(), False)    # Sanity Check
        self.assertEqual(r1, [(1, datetime_format)])

    def test_get_available_sold_out(self):
        show = self.show[2]
        occ = self.occ[2]

        r = Occurrence.objects.get_available(show)

        self.assertEqual(show.show_sold_out(), True)    # Sanity Check
        self.assertEqual(occ.sold_out(), True)

        self.assertEqual(r, [])

    def test_show_sales(self):
        self.assertEqual(self.show[1].get_sale_data()['show_sales'], 1)

    def test_get_available_show_closed(self):
        r = Occurrence.objects.get_available(self.show[3])
        self.assertEqual(r, [])

    def test_get_available_show_show_closed(self):
        r = Occurrence.objects.get_available_show(self.show[3])
        self.assertNotEqual(r, [])


class SaleTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name='Test Category', slug='test', sort=1)
        today = date.today()
        now = datetime.now()
        loc = 'Location 1'
        desc = 'A show somewhere'
        l_desc = 'A longer show somewhere'
        poster = File(open('test/test_poster.jpg'))

        # Create some good shows
        cls.show = Show.objects.create(name='S1', category=cat, location=loc, description='show current',
                                       long_description=l_desc, poster=poster, start_date=today, end_date=today + timedelta(days=6))
        # cls.show{2} = Show.objects.create(name='S2', category=cls.cat,
        # location=cls.loc, description='show past', long_description=cls.l_desc,
        # start_date=cls.today - timedelta(days=6), end_date=cls.today)

        # Create an occurrence
        cls.occ = Occurrence.objects.create(show=cls.show, date=today, time=datetime.now(
        ) + timedelta(hours=3), maximum_sell=80, hours_til_close=2)

        cls.ticket = Ticket.objects.create(
            occurrence=cls.occ,
            person_name='testman',
            email_address='test@test.com',
            quantity=1,
        )

        cls.sale = Sale.objects.create(occurrence=cls.occ, ticket='None', number=18, price=53,
                                       number_concession=2,
                                       number_member=2,
                                       number_public=2,
                                       number_season=2,
                                       number_season_sale=2,
                                       number_fellow=2,
                                       number_fringe=2,
                                       number_matinee_freshers=2,
                                       number_matinee_freshers_nnt=2,
                                       )

    def test_show_sales(self):
        profit = self.show.get_sale_data()['show_sales']
        self.assertEqual(profit, 53)

    def test_total_tickets_sold_show(self):
        tickets = self.show.get_sale_data()['total_sold']
        self.assertEqual(tickets, 18)

    def test_total_tickets_reserved(self):
        reserved = self.show.get_sale_data()['total_reserved']
        self.assertEqual(reserved, 1)

    def test_total_possible(self):
        total = self.show.get_sale_data()['total_possible']
        self.assertEqual(total, 80)

    def test_tallys(self):
        occ = self.occ
        concession = occ.get_tally('concession')
        member = occ.get_tally('member')
        public = occ.get_tally('public')
        season = occ.get_tally('season')
        season_sale = occ.get_tally('season_sale')
        fellow = occ.get_tally('fellow')
        fringe = occ.get_tally('fringe')
        mat_f = occ.get_tally('matinee_freshers')
        mat_f_nnt = occ.get_tally('matinee_freshers_nnt')

        tot = concession + member + public + season + \
            season_sale + fellow + fringe + mat_f + mat_f_nnt

        self.assertEqual(tot, 18)

    def test_collected(self):
        occ = self.occ
        Ticket.objects.create(
            occurrence=occ,
            person_name='testman2',
            email_address='test@test.com',
            quantity=1,
            collected=1
        )

        coll = Ticket.objects.get_collected(occurrence=occ)

        self.assertEqual(coll, 1)

    def test_sold_not_reserved(self):
        occ = self.occ

        Sale.objects.create(occurrence=occ, ticket='testman', number=18, price=53,
                            number_concession=2,
                            number_member=2,
                            number_public=2,
                            number_season=2,
                            number_season_sale=2,
                            number_fellow=2,
                            number_fringe=2,
                            number_matinee_freshers=2,
                            number_matinee_freshers_nnt=2,
                            )

        sold = Sale.objects.sold_not_reserved(occurrence=occ)

        self.assertEqual(sold, 18)
