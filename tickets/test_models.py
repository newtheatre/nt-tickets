from django.test import TestCase
from django.core.files import File
from models import *
from markdown2 import Markdown

from datetime import date, timedelta, datetime



class StaticPageTest(TestCase):

    def test_list_view(self):
        response = self.client.get('/list/')
        self.assertEqual(response.status_code, 200)

    def test_sidebar_view(self):
        response = self.client.get('/sidebar/')
        self.assertEqual(response.status_code, 200)


class BookTest(TestCase):

    def setUp(self):
        cat = Category.objects.create(name='Test Category', slug='test', sort=1)
        start_date = date.today() + timedelta(days=2)
        end_date = date.today() + timedelta(days=5)
        Show.objects.create(
            name='Test Show',
            location='Somewhere',
            description='Some Info',
            long_description='Some more info',
            poster=File(open('test/test_poster.jpg')),
            start_date=start_date,
            end_date=end_date,
            category=cat
            )
    def test_category_name(self):
        cat = Category.objects.get(pk=1).__str__()
        self.assertEqual(cat, 'Test Category')

    def test_show_exists(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.name, 'Test Show')

    def test_book_form(self):
        response = self.client.get('/book/1/')
        self.assertEqual(response.status_code, 200)

    def test_show_sold_out_false(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.show_sold_out(), False)

    def test_has_occurrences_false(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.has_occurrences(), False)


class ShowTest(TestCase):

    # fixtures = ['test/test_sales.json']

    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name='Test Category', slug='test', sort=1)
        cls.today = date.today()
        cls.loc = 'Location 1'
        cls.desc = 'A show somewhere'
        cls.l_desc = 'A longer show somewhere'
        cls.poster = File(open('test/test_poster.jpg'))

        # Create some good shows

        cls.show = Show.objects.create(name='S1', category=cls.cat, location=cls.loc, description='show current', long_description=cls.l_desc, poster=cls.poster, start_date=cls.today, end_date=cls.today + timedelta(days=6))
        # cls.show{2} = Show.objects.create(name='S2', category=cls.cat, location=cls.loc, description='show past', long_description=cls.l_desc, start_date=cls.today - timedelta(days=6), end_date=cls.today)

        # Create an occurrence 
        cls.occ = Occurrence.objects.create(show=cls.show, date=cls.today, time=datetime.now() + timedelta(hours=4), maximum_sell=2, hours_til_close=2)

        cls.ticket = Ticket.objects.create(
            occurrence= cls.occ,
            stamp=datetime.now(),
            person_name='testman',
            email_address='test@test.com',
            quantity=1,
            cancelled=False,
            collected=False
            )

        cls.sale = Sale.objects.create(occurrence=cls.occ, ticket='', price=1, number=2)

    def test_is_current_false(self):
        show = self.show
        show.end_date = date.today() + timedelta(days=-5)
        self.assertEqual(show.is_current(), False)

    def test_sold_out_true(self):
        show = self.show
        occ = self.occ
        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.now(),
            person_name='testman2',
            email_address='test@test.com',
            quantity=1,
            cancelled=False,
            unique_code=rand_16(),
            )

        self.assertEqual(show.show_sold_out(), True)
        self.assertEqual(occ.sold_out(), True)

    def test_sold_out_false(self):
        show = Show.objects.get(pk=1)
        occ = Occurrence.objects.get(pk=1)
        self.assertEqual(occ.sold_out(), False)
        self.assertEqual(show.show_sold_out(), False)

    def test_has_occurrences_true(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.has_occurrences(), True)

    def test_show_name(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.__str__(), show.name)

    def test_markdown(self):
        show = Show.objects.get(pk=1)
        ld_md = '<p>A longer show somewhere</p>\n'
        self.assertEqual(show.long_markdown(), ld_md)

    def test_datetime_formatted(self):
        occ = Occurrence.objects.get(pk=1)
        day_format = occ.date.strftime('%A')
        time_format = occ.time.strftime('%-I:%M %p').lower()
        datetime_format = occ.date.strftime('%A %d %B ') + \
            occ.time.strftime('%-I%p').lower()

        self.assertEqual(occ.day_formatted(), day_format)
        self.assertEqual(occ.time_formatted(), time_format)
        self.assertEqual(occ.datetime_formatted(), datetime_format)

    def test_occurrence_str(self):
        occ = Occurrence.objects.get(pk=1)
        occ_str = occ.show.name + \
            " on " + str(occ.date) + \
            " at " + str(occ.time)
        self.assertEqual(occ.__str__(), occ_str)

    def test_ticket_str(self):
        tick = Ticket.objects.get(pk=1)
        tick_str = tick.occurrence.show.name + \
            " on " + str(tick.occurrence.date) + \
            " at " + str(tick.occurrence.time) + \
            " for " + tick.person_name

        self.assertEqual(tick.__str__(), tick_str)

    def test_get_available(self):
        show = Show.objects.get(pk=1)
        occ = Occurrence.objects.get(pk=1)
        datetime_format = occ.date.strftime('%A %d %B ') + \
            occ.time.strftime('%-I%p').lower()

        r1 = Occurrence.objects.get_available(show)

        self.assertEqual(r1, [(1, datetime_format)])

    def test_get_available_sold_out(self):
        show = Show.objects.get(pk=1)
        occ = Occurrence.objects.get(pk=1)
        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.now(),
            person_name='testman2',
            email_address='test@test.com',
            quantity=79,
            cancelled=False,
            unique_code=rand_16(),
            )


        r = Occurrence.objects.get_available(show)

        self.assertEqual(show.show_sold_out(), True)    # Sanity Check
        self.assertEqual(occ.sold_out(), True)

        self.assertEqual(r, [])

    def test_show_sales(self):
        show = Show.objects.get(pk=1)
        occ = Occurrence.objects.get(pk=1)

        self.assertEqual(show.show_sales(), 1)

class ShowClosed(TestCase):
    def setUp(self):
        cat = Category.objects.create(name='Test Category', slug='test', sort=1)
        start_date = date.today() + timedelta(days=2)
        end_date = date.today() + timedelta(days=5)
        Show.objects.create(
            name='Test Show',
            location='Somewhere',
            description='Some Info',
            long_description='Some more info',
            poster=File(open('test/test_poster.jpg')),
            start_date=start_date,
            end_date=end_date,
            category=cat
            )

        Occurrence.objects.create(
            show=Show.objects.get(pk=1),
            date=date.today(),
            time=datetime.now(),
            maximum_sell=2,
            hours_til_close=2,
            unique_code=rand_16(),
            )

        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.now(),
            person_name='testman',
            email_address='test@test.com',
            quantity=1,
            cancelled=False,
            unique_code=rand_16(),
            )

    def test_get_available_show_closed(self):
        show = Show.objects.get(pk=1)
        occ = Occurrence.objects.get(pk=1)

        r = Occurrence.objects.get_available(show)

        self.assertEqual(r, [])