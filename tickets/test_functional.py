from django.test import LiveServerTestCase, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.core.management import call_command
import time
import factory
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.core.files import File
from django.template.defaultfilters import slugify
from tickets import models
from pricing import models

from django.conf import settings

import datetime
import os


def UserFactory():
    User.objects.create_superuser(
        username='Jim',
        email='jim@rash.com',
        password='correcthorsebatterystaple',
    )


def createCategory(*args, **kwargs):
    name = kwargs.get('name', 'In House')
    cat, created = models.Category.objects.get_or_create(
        name=name,
        slug=slugify(name),
        sort=kwargs.get('sort', 1)
    )

    return cat


def createShow(*args, **kwargs):
    show, created = models.Show.objects.get_or_create(
        name=kwargs.get('name', 'Test Show'),
        location='Somewhere',
        description='Test show present',
        long_description='Some more info',

        start_date=kwargs.get('start_date', datetime.date.today()),
        end_date=kwargs.get('end_date', datetime.date.today() + datetime.timedelta(days=5)),

        category=kwargs.get('category', createCategory())
    )

    return show


def createOccurrence(*args, **kwargs):
    occ, created = models.Occurrence.objects.get_or_create(
        show=kwargs.get('show', createShow()),
        date=kwargs.get('date', datetime.date.today() + datetime.timedelta(days=1)),
        time=kwargs.get('time', "19:30"),
        maximum_sell=kwargs.get('maximum_sell', 2),
        hours_til_close=kwargs.get('hours_til_close', 2)
    )

    return occ


def createTicket(*args, **kwargs):
    tick = models.Ticket.objects.create(
        occurrence=kwargs.get('occurrence', createOccurrence()),
        person_name='Test Person',
        email_address='test@person.com',
        quantity=kwargs.get('quantity', 2),
        collected=kwargs.get('collected', False),
        cancelled=kwargs.get('cancelled', False)
    )

    return tick


class BookTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('bin/chromedriver')
        self.browser.implicitly_wait(10)

        self.show1 = createShow(
            name="TS In House")
        self.occ1 = createOccurrence(show=self.show1)
        self.occ2 = createOccurrence(
            show=self.show1, date=datetime.date.today() + datetime.timedelta(days=2))

    def tearDown(self):
        self.browser.quit()

    def test_book_show_quick(self):

        self.browser.get(self.live_server_url + '/book/' + str(self.show1.id))

        # Check the title is correct
        title_text = self.browser.find_element_by_xpath('//p[1]').text
        self.assertIn(
            title_text,
            'You\'re booking tickets for ' + self.show1.name + ' at Somewhere.'
        )

        # Input correct details
        occurrence = Select(self.browser.find_element_by_id('id_occurrence'))
        occurrence.select_by_value(str(self.occ1.id))
        quantity = Select(self.browser.find_element_by_id('id_quantity'))
        quantity.select_by_value('1')
        name = self.browser.find_element_by_id('id_person_name')
        name.send_keys('Test Name1')
        email = self.browser.find_element_by_id('id_email_address')
        email.send_keys('test@test.com')

        # Submit the form
        self.browser.find_element_by_id('submit-btn').click()
        # Wait a little for the page to load
        self.browser.implicitly_wait(10)
        thanks_title = self.browser.find_element_by_xpath('//div[@class="main"]/h1').text
        self.assertEqual(thanks_title, 'Thanks!')
        self.assertEqual(
            self.live_server_url + '/book/' + str(self.show1.id) + '/thanks/',
            self.browser.current_url
        )

        # Navigate back to booking
        self.browser.get(self.live_server_url + '/book/' + str(self.show1.id))

        # Submit another form with the same details
        occurrence = Select(self.browser.find_element_by_id('id_occurrence'))
        occurrence.select_by_value(str(self.occ1.id))
        quantity = Select(self.browser.find_element_by_id('id_quantity'))
        quantity.select_by_value('1')
        name = self.browser.find_element_by_id('id_person_name')
        name.send_keys('Test Name1')
        email = self.browser.find_element_by_id('id_email_address')
        email.send_keys('test@test.com')

        # Submit the form
        self.browser.find_element_by_id('submit-btn').click()
        # Wait for the page to load
        self.browser.implicitly_wait(10)
        error_title = self.browser.find_element_by_xpath('//div[@class="main"]/h1').text
        # Should get an error
        self.assertEqual(error_title, 'Error')

        # Wait to be allowed to book tickets again
        time.sleep(6)
        # Navigate to the boking page
        self.browser.get(self.live_server_url + '/book/' + str(self.show1.id))

        # Submit another form with the same details
        occurrence = Select(self.browser.find_element_by_id('id_occurrence'))
        occurrence.select_by_value(str(self.occ1.id))
        quantity = Select(self.browser.find_element_by_id('id_quantity'))
        quantity.select_by_value('1')
        name = self.browser.find_element_by_id('id_person_name')
        name.send_keys('Test Name1')
        email = self.browser.find_element_by_id('id_email_address')
        email.send_keys('test@test.com')

        # Submit the form
        self.browser.find_element_by_id('submit-btn').click()
        # Wait for the page to load
        self.browser.implicitly_wait(10)

        # Make sure we are allowed to book tickets
        thanks_title = self.browser.find_element_by_xpath('//div[@class="main"]/h1').text
        self.assertEqual(thanks_title, 'Thanks!')
        self.assertEqual(
            self.live_server_url + '/book/' + str(self.show1.id) + '/thanks/',
            self.browser.current_url
        )

    def test_book_show_no_date(self):
        browser = self.browser
        browser.get(self.live_server_url + '/book/' + str(self.show1.id))

        # Input correct details but no date or seats
        name = browser.find_element_by_id('id_person_name')
        name.send_keys('Test Name1')
        email = browser.find_element_by_id('id_email_address')
        email.send_keys('test@test.com')

        # Submit the form
        browser.find_element_by_id('submit-btn').click()
        # Wait a little bit
        # self.browser.implicitly_wait(10)
        occurrence_err = browser.find_element_by_xpath(
            '//form[@class="submit-once"]/div[@class="col col_left"]/div[@class="control-group error required"][1]/div[@class="controls"]/p[@class="help-block"]'
        ).text
        self.assertEqual(occurrence_err, 'This field is required.')

    def test_book_one_sold_out(self):

        self.tick = TicketFactory.create(occurrence=self.occ2, quantity=2)

        self.browser.get(self.live_server_url + '/book/' + str(self.show1.id))

        options = len(self.browser.find_elements_by_xpath(
            '//select[@id="id_occurrence"]'))
        self.assertEqual(options, 1)


class ListTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('bin/chromedriver')

        self.show1 = createShow(
            name="TS In House")
        self.occ1 = createOccurrence(show=self.show1)

    def tearDown(self):
        self.browser.quit()

    def test_list_view(self):
        self.browser.get(self.live_server_url + '/list')

        # Check that we have a title
        self.browser.implicitly_wait(3)
        title_text = self.browser.find_element_by_id('show-title').text
        self.assertEqual(title_text, self.show1.name)


class AuthTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('bin/chromedriver')
        self.browser.set_window_size(1200, 1000)
        self.browser.implicitly_wait(5)
        UserFactory()

    def tearDown(self):
        self.browser.quit()

    def test_login_correct(self):
        self.browser.get(self.live_server_url + '/')

        # Test that we've actually got a login page
        self.assertIn('login', self.browser.current_url)

        username = self.browser.find_element_by_id('username')
        username.send_keys('Jim')
        password = self.browser.find_element_by_id('password')
        # Send the wrong password
        password.send_keys('correcthorsebatterystapleerror')

        # Submit the form

        submit = self.browser.find_element_by_id('submit')
        submit.click()

        error_text = self.browser.find_element_by_xpath('//p[@class="red-text"]').text
        # Make sure we got an error
        self.assertIn('incorrect', error_text)

        # Test that we're still on the login page
        self.assertIn('login', self.browser.current_url)

        username = self.browser.find_element_by_id('username')
        username.send_keys('Jim')
        password = self.browser.find_element_by_id('password')
        # Send the correct password
        password.send_keys('correcthorsebatterystaple')

        # Submit the form
        submit = self.browser.find_element_by_id('submit')
        submit.click()

        nav_text = self.browser.find_element_by_xpath(
            '//a[@class="dropdown-button"]').text
        # Check the username is in the nav
        self.assertIn('Jim', nav_text)

        # Test login page with authenticated user
        self.browser.get(self.live_server_url + '/login/')

        nav_text = self.browser.find_element_by_xpath(
            '//a[@class="dropdown-button"]').text
        # Check the username is in the nav
        self.assertIn('Jim', nav_text)

        # Test login page with a page request with authenticated user
        self.browser.get(self.live_server_url + '/login/?Pnext=/')

        nav_text = self.browser.find_element_by_xpath(
            '//a[@class="dropdown-button"]').text
        # Check the username is in the nav
        self.assertIn('Jim', nav_text)

        # test that we can logout as well
        self.browser.get(self.live_server_url + '/logout/')

        logout = self.browser.find_element_by_xpath(
            '//h4[@class="light nnt-orange medium-text"]').text
        self.assertEqual(logout, 'Logged Out')


class IndexTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('bin/chromedriver')
        # Force desktop sizing
        self.browser.set_window_size(1200, 1000)

        UserFactory()

        self.show1 = createShow(
            name="TS In House")
        self.occ1 = createOccurrence(show=self.show1)

    def tearDown(self):
        self.browser.quit()

    def test_index(self):
        self.browser.get(self.live_server_url + '/')

        # Login
        username = self.browser.find_element_by_id('username')
        username.send_keys('Jim')
        password = self.browser.find_element_by_id('password')
        # Send the wrong password
        password.send_keys('correcthorsebatterystaple')

        # Submit the form
        submit = self.browser.find_element_by_id('submit')
        submit.click()

        title = self.browser.find_element_by_id('title').text
        self.assertEqual(title, self.show1.name)

        self.browser.get(self.live_server_url + '/?page=10')

        page = self.browser.find_element_by_css_selector('h1').text
        self.assertIn('404', page)


class ReportTest(StaticLiveServerTestCase):

    def setUp(self):
        call_command('create_pricing')

        self.browser = webdriver.Chrome('bin/chromedriver')
        # Force desktop sizing
        self.browser.set_window_size(1200, 1000)

        self.browser.implicitly_wait(10)

        UserFactory()

        self.show1 = createShow(
            name="TS In House")
        self.occ1 = createOccurrence(show=self.show1, maximum_sell=80)

    def tearDown(self):
        self.browser.quit()

    def test_report(self):
        self.browser.get(self.live_server_url + '/')

        # Login
        username = self.browser.find_element_by_id('username')
        username.send_keys('Jim')
        password = self.browser.find_element_by_id('password')
        # Send the wrong password
        password.send_keys('correcthorsebatterystaple')

        # Submit the form
        submit = self.browser.find_element_by_id('submit')
        submit.click()

        # Navigate to the sale page
        img = self.browser.find_element_by_xpath(
            '//div[@class="card small grey darken-3"][1]//img[@id="report-image"]')
        img.click()

        # Get the choose showing modal
        showing = self.browser.find_element_by_xpath(
            '//div[@class="col s6 center-align"][1]/button')
        showing.click()

        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.element_to_be_clickable((By.ID, 'picker-modal')))

        modal = self.browser.find_element_by_id('picker-modal')
        self.assertTrue(modal.is_displayed())

        occ = self.browser.find_element_by_id('showing')
        occ.click()

        free_text = self.browser.find_element_by_xpath('//div[@id="sale-update"]//p').text
        self.assertIn('No tickets sold', free_text)
        self.assertIn('No tickets reserved', free_text)
        self.assertIn('80 tickets left', free_text)

        # Check selling tickets adds up properly
        pricing = models.InHousePricing.objects.get(id=1)
        member_price = pricing.member_price
        concession_price = pricing.concession_price
        public_price = pricing.public_price
        mat_f_price = pricing.matinee_freshers_price
        mat_f_nnt_price = pricing.matinee_freshers_nnt_price

        out = self.browser.find_element_by_id('out1').text

        member = self.browser.find_element_by_id('member')
        action = ActionChains(self.browser)
        action.click(on_element=member)
        action.send_keys('1')
        action.key_down(Keys.CONTROL)
        action.key_up(Keys.CONTROL)
        action.perform()
        # member.click()
        # member.send_keys('1')
        # member.send_keys('tab')


class SaleTest(StaticLiveServerTestCase):

    def __init__(self, *args, **kwargs):
        super(SaleTest, self).__init__(*args, **kwargs)
        if settings.DEBUG == False:
            settings.DEBUG = True

    def setUp(self):
        call_command('create_pricing')
        call_command('create_categories')

        self.browser = webdriver.Chrome('bin/chromedriver')
        # Force desktop sizing
        self.browser.set_window_size(1200, 1000)

        self.browser.implicitly_wait(10)

        self.user = User.objects.create_superuser(
            username='Jim', password='Rash', email='jim@rash.com',)
        self.user.save()

        self.in_house = models.Category.objects.get(slug='in-house')
        self.fringe = models.Category.objects.get(slug='fringe')
        self.external = models.Category.objects.get(slug='external')
        self.stuff = models.Category.objects.get(slug='stuff')

        # In House Show
        self.show1 = createShow(name='TS In House', category=self.in_house)
        self.occ1 = createOccurrence(maximum_sell=80, show=self.show1, time='08:00')
        self.occ1_2 = createOccurrence(
            maximum_sell=80, show=self.show1, time='14:30')
        self.occ1_3 = createOccurrence(maximum_sell=10, show=self.show1, time='09:00')
        self.occ1_4 = createOccurrence(maximum_sell=10, show=self.show1, time='10:00')
        self.reserv1 = {
            1: createTicket(occurrence=self.occ1, quantity=10),
            2: createTicket(occurrence=self.occ1, quantity=10),
            3: createTicket(occurrence=self.occ1, quantity=10, collected=True),
            4: createTicket(occurrence=self.occ1, quantity=10, cancelled=True),
            5: createTicket(occurrence=self.occ1_2, quantity=10),
            6: createTicket(occurrence=self.occ1_4, quantity=5),
            7: createTicket(occurrence=self.occ1_4, quantity=5),
        }

        # Fringe Show
        self.show2 = createShow(name="TS Fringe", category=self.fringe)
        self.occ2 = createOccurrence(maximum_sell=80, show=self.show2)
        self.reserv2 = createTicket(occurrence=self.occ2, quantity=10)

        # External Show
        self.show3 = createShow(name="TS External 1", category=self.external)
        self.occ3 = createOccurrence(maximum_sell=80, show=self.show3)
        self.exprice1 = models.ExternalPricing.objects.create(
            show=self.show3, allow_season_tickets=False, allow_fellow_tickets=False)
        self.reserv3 = createTicket(occurrence=self.occ3, quantity=10)

        # StuFF Show
        self.show4 = createShow(name="TS StuFF", category=self.stuff)
        self.occ4 = createOccurrence(maximum_sell=80, show=self.show4)
        self.stprice = models.StuFFPricing.objects.create(show=self.show4)
        self.reserv4 = createTicket(occurrence=self.occ4, quantity=10)

    def tearDown(self):
        self.browser.quit()

    def authenticate(self, n=None):
        self.assertIn(
            self.live_server_url + '/login/', self.browser.current_url)
        if n:
            self.assertIn('?next=%s' % n, self.browser.current_url)
            username = self.browser.find_element_by_id('username')
            password = self.browser.find_element_by_id('password')
            submit = self.browser.find_element_by_id('submit')

            username.send_keys("Jim")
            password.send_keys("Rash")
            submit.click()

        self.assertEqual(self.live_server_url + n, self.browser.current_url)

    def checkInput(self, name, price, number=1):
        submit = self.browser.find_element_by_id('sell_button')

        self.assertTrue(submit.get_attribute('disabled'))

        check = self.browser.find_element_by_id(name)
        check.click()
        check.send_keys(number)

        self.assertFalse(submit.get_attribute('disabled'))
        total1 = self.browser.find_element_by_id('out1').text
        time.sleep(0.2)
        self.assertEqual(total1, price)

        sale = 0
        total2 = self.browser.find_element_by_id('final').text
        sale = float(total2) + float(price)

        submit.click()
        time.sleep(0.2)  # Wait a little bit for things to happen
        total3 = self.browser.find_element_by_id('final').text
        self.assertEqual(sale, float(total3))

    def checkOutput(self, number, occ):
        sold = self.browser.find_element_by_id('sold').text
        reserved = self.browser.find_element_by_id('reserved').text
        left = self.browser.find_element_by_id('left').text

        self.assertEqual(int(sold), number)
        self.assertEqual(int(reserved), occ.tickets_sold())
        self.assertEqual(int(left), occ.maximum_sell - number - occ.tickets_sold())

    def checkDiasbled(self):
        submit = self.browser.find_element_by_id('sell_button')
        self.assertTrue(submit.get_attribute('disabled'))
        check = self.browser.find_element_by_id('member')
        check.click()
        check.send_keys('1')
        self.assertTrue(submit.get_attribute('disabled'))

    def test_sale(self):
        # Requests address
        self.browser.get(self.live_server_url + '/')
        # Gets redirected to login
        self.authenticate('/')

        # Navigate to in house show page
        self.browser.get(
            self.live_server_url + '/show/' +
            str(self.show1.id) + '/' + str(self.occ1.id))

        # Check that selling tickets does the things it should
        self.checkInput('member', '5.00')
        self.checkInput('concession', '5.00')
        self.checkInput('public', '8.00')
        self.checkInput('season', '0.00')
        self.checkInput('season_sales', '40.00')
        self.checkInput('season_sales_nnt', '20.00')
        self.checkInput('fellow', '0.00')

        self.checkOutput(7, self.occ1)

        # Navigate to in house matinee show page
        self.browser.get(
            self.live_server_url + '/show/' +
            str(self.show1.id) + '/' + str(self.occ1_2.id))

        self.checkInput('matinee_freshers', '2.50')
        self.checkInput('matinee_freshers_nnt', '2.00')

        self.checkOutput(2, self.occ1_2)

        # Navigate to fringe show page
        self.browser.get(
            self.live_server_url + '/show/' +
            str(self.show2.id) + '/' + str(self.occ2.id))

        self.checkInput('fringe', '3.00')
        self.checkInput('season', '0.00')
        self.checkInput('season_sales', '40.00')
        self.checkInput('season_sales_nnt', '20.00')
        self.checkInput('fellow', '0.00')

        self.checkOutput(5, self.occ2)

        # Navigate to external show page
        self.browser.get(
            self.live_server_url + '/show/' +
            str(self.show3.id) + '/' + str(self.occ3.id))

        self.checkInput('member', '5.00')
        self.checkInput('concession', '5.00')
        self.checkInput('public', '8.00')

        self.checkOutput(3, self.occ3)

        # Navigate to stuff page
        self.browser.get(
            self.live_server_url + '/show/' +
            str(self.show4.id) + '/' + str(self.occ4.id))

        self.checkInput('stuff', '5.00')

        self.checkOutput(1, self.occ4)

    def test_sale_reservations(self):
        # Check selling reserved tickets acts as it should
        # Selling all the tickets
        # Requests address
        self.browser.get(self.live_server_url + '/')
        # Gets redirected to login
        self.authenticate('/')

        # Navigate to in house show page
        self.browser.get(
            self.live_server_url + '/show/' +
            str(self.show1.id) + '/' + str(self.occ1.id))

        reservation = self.browser.find_element_by_id('reserve_button')
        reservation.click()

        add1 = self.browser.find_element_by_xpath('//form[@id="reserve_1"]/button')
        add2 = self.browser.find_element_by_xpath('//form[@id="reserve_2"]/button')
        add3 = self.browser.find_element_by_id('add_button_3')
        add4 = self.browser.find_element_by_id('add_button_4')

        # Check that the correct buttons are enabled
        self.assertFalse(add1.get_attribute('disabled'))
        self.assertFalse(add2.get_attribute('disabled'))
        self.assertTrue(add3.get_attribute('disabled'))
        self.assertTrue(add4.get_attribute('disabled'))

        # Add the first set of tickets to the form
        add1.click()

        # Check we can't sell tickets unless we sell the same number as on the reservation
        time.sleep(1)
        self.checkDiasbled()

        # Sell the same number of tickets as on the reservation
        time.sleep(1)
        self.checkInput('member', '50.00', 10)

        reservation.click()
        time.sleep(1)
        # Reduce the number of tickets collected by 1
        less = self.browser.find_element_by_id('less_2')
        less.click()

        # Add this to the form
        add2 = self.browser.find_element_by_xpath('//form[@id="reserve_2"]/button')
        add2.click()

        time.sleep(1)
        self.checkDiasbled()

        # Sell the same number of tickets as on the reservation
        self.checkInput('member', '45.00', 9)

        # Check that we can sell the remaining ticket
        self.checkInput('member', '5.00', 1)

    def test_sale_sold_out(self):
        # Check selling tickets when shows are sold out
        # No reservations
        # Requests address
        self.browser.get(self.live_server_url + '/')
        # Gets redirected to login
        self.authenticate('/')

        self.browser.get(
            self.live_server_url + '/show/' +
            str(self.show1.id) + '/' + str(self.occ1_3.id))

        self.checkInput('member', '50.00', 10)

        # Check that we can't sell any tickets now they're all sold
        self.checkDiasbled()

        # Some reservations
        self.browser.get(
            self.live_server_url + '/show/' +
            str(self.show1.id) + '/' + str(self.occ1_4.id))

        self.checkDiasbled()

        reservation = self.browser.find_element_by_id('reserve_button')
        reservation.click()

        time.sleep(1)
        add = self.browser.find_element_by_xpath('//form[@id="reserve_1"]/button')
        add.click()

        time.sleep(1)
        self.checkDiasbled()

        self.checkInput('member', '25.00', 5)
        self.checkDiasbled()

        reservation.click()

        time.sleep(1)
        # Reduce the number of tickets collected by 1
        less = self.browser.find_element_by_id('less_2')
        less.click()
        # Add this to the form
        add2 = self.browser.find_element_by_xpath('//form[@id="reserve_2"]/button')
        add2.click()

        time.sleep(1)
        self.checkInput('member', '20.00', 4)

        # Check that we can sell the remaining ticket
        self.checkInput('member', '5.00', 1)

        self.checkDiasbled()
