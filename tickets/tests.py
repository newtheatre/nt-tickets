from django.test import TestCase
from django.core.files import File
from models import *

import datetime


class StaticPageTest(TestCase):

    def test_list_view(self):
        response = self.client.get('/list/')
        self.assertEqual(response.status_code, 200)

    def test_sidebar_view(self):
        response = self.client.get('/sidebar/')
        self.assertEqual(response.status_code, 200)


class BookTest(TestCase):

    def setUp(self):
        cat = Category.objects.create(name='Test Category',slug='test',sort=1)
        start_date = datetime.date.today()+datetime.timedelta(days=2)
        end_date = datetime.date.today()+datetime.timedelta(days=5)
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

    def test_show_exists(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.name, 'Test Show')

    def test_book_form(self):
        response = self.client.get('/book/1/')
        self.assertEqual(response.status_code, 200)

    def has_occurrences_false(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.has_occurrences(), False)


class ShowTest(TestCase):

    def setUp(self):
        cat = Category.objects.create(name='Test Category',slug='test',sort=1)
        start_date = datetime.date.today()+datetime.timedelta(days=2)
        end_date = datetime.date.today()+datetime.timedelta(days=5)
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
            date=datetime.date.today(),
            time=datetime.datetime.now(),
            maximum_sell=2,
            hours_til_close=2,
            unique_code=rand_16(),
            )

        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.datetime.now(),
            person_name='testman',
            email_address='test@test.com',
            quantity=1,
            cancelled=False,
            unique_code=rand_16(),
            )

    def test_is_current_false(self):
        show = Show.objects.get(pk=1)
        show.end_date = datetime.date.today() + datetime.timedelta(days=-5)
        self.assertEqual(show.is_current(), False)

    def test_sold_out_false(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.sold_out(), False)

    def test_sold_out_true(self):
        show = Show.objects.get(pk=1)
        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.datetime.now(),
            person_name='testman',
            email_address='test@test.com',
            quantity=1,
            cancelled=False,
            unique_code=rand_16(),
            )
        self.assertEqual(show.sold_out(), True)

    def has_occurrences_true(self):
        show = Show.objects.get(pk=2)
        self.assertEqual(show.has_occurrences(), True)
