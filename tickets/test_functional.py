from django.test import LiveServerTestCase
from django.contrib.auth.models import User
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from django.core.files import File
from tickets.models import *

import datetime
import os


class BookTest(LiveServerTestCase):

  def setUp(self):
    self.browser = webdriver.Chrome('bin/chromedriver')

    cat = Category.objects.create(name='Test Category', slug='test', sort=1)
    start_date = datetime.date.today() + datetime.timedelta(days=2)
    end_date = datetime.date.today() + datetime.timedelta(days=5)

    # Create shows
    Show.objects.create(
      name='Test Show',
      location='Somewhere',
      description='Test show present',
      long_description='Some more info',
      poster=File(open('test/test_poster.jpg')),
      start_date=start_date,
      end_date=end_date,
      category=cat
      )

    # Create an occurrence
    Occurrence.objects.create(
      show=Show.objects.get(name='Test Show'),
      date=start_date,
      time=datetime.datetime.now(),
      maximum_sell=2,
      hours_til_close=2,
      unique_code=rand_16(),
      )

  def tearDown(self):
    self.browser.quit()

  def test_book_show_quick(self):
    browser = self.browser
    show_id = Show.objects.get(name='Test Show').id
    browser.get(self.live_server_url + '/book/' + str(show_id))

    # Check the title is correct
    title_text = browser.find_element_by_xpath(
      '//p[1]'
      ).text
    self.assertIn(
      title_text,
      'You\'re booking tickets for Test Show at Somewhere.'
      )

    # Input correct details
    occurrence = occurrence = Select(browser.find_element_by_id('id_occurrence'))
    occurrence.select_by_value(str(show_id))
    quantity = Select(browser.find_element_by_id('id_quantity'))
    quantity.select_by_value('1')
    name = browser.find_element_by_id('id_person_name')
    name.send_keys('Test Name1')
    email = browser.find_element_by_id('id_email_address')
    email.send_keys('test@test.com')

    # Submit the form
    browser.find_element_by_id('submit-btn').click()
    # Wait a little for the page to load
    browser.implicitly_wait(10)
    thanks_title = browser.find_element_by_xpath('//div[@class="main"]/h1').text
    self.assertEqual(thanks_title, 'Thanks!') 
    self.assertEqual(
      self.live_server_url + '/book/' + str(show_id) + '/thanks/',
      browser.current_url
      )

    # Navigate back to booking
    browser.get(self.live_server_url + '/book/' + str(show_id))

    # Submit another form with the same details
    occurrence = Select(browser.find_element_by_id('id_occurrence'))
    occurrence.select_by_value(str(show_id))
    quantity = Select(browser.find_element_by_id('id_quantity'))
    quantity.select_by_value('1')
    name = browser.find_element_by_id('id_person_name')
    name.send_keys('Test Name1')
    email = browser.find_element_by_id('id_email_address')
    email.send_keys('test@test.com')

    # Submit the form
    browser.find_element_by_id('submit-btn').click()
    # Wait for the page to load
    browser.implicitly_wait(10)
    error_title = browser.find_element_by_xpath('//div[@class="main"]/h1').text
    # Should get an error
    self.assertEqual(error_title, 'Error')

    # Wait to be allowed to book tickets again
    time.sleep(6)
    # Navigate to the boking page
    browser.get(self.live_server_url + '/book/' + str(show_id))

    # Submit another form with the same details
    occurrence = Select(browser.find_element_by_id('id_occurrence'))
    occurrence.select_by_value(str(show_id))
    quantity = Select(browser.find_element_by_id('id_quantity'))
    quantity.select_by_value('1')
    name = browser.find_element_by_id('id_person_name')
    name.send_keys('Test Name1')
    email = browser.find_element_by_id('id_email_address')
    email.send_keys('test@test.com')

    # Submit the form
    browser.find_element_by_id('submit-btn').click()
    # Wait for the page to load
    browser.implicitly_wait(10)

    # Make sure we are allowed to book tickets
    thanks_title = browser.find_element_by_xpath('//div[@class="main"]/h1').text
    self.assertEqual(thanks_title, 'Thanks!') 
    self.assertEqual(
      self.live_server_url + '/book/' + str(show_id) + '/thanks/',
      browser.current_url
      )


  def test_book_show_no_date(self):
    browser = self.browser
    show_id = Show.objects.get(name='Test Show').id
    browser.get(self.live_server_url + '/book/' + str(show_id))

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


class ListTest(LiveServerTestCase):

  def setUp(self):
    self.browser = webdriver.Chrome('bin/chromedriver')

    cat = Category.objects.create(name='Test Category', slug='test', sort=1)
    start_date = datetime.date.today() + datetime.timedelta(days=2)
    end_date = datetime.date.today() + datetime.timedelta(days=5)

    # Create a show
    Show.objects.create(
      name='Test Show',
      location='Somewhere',
      description='Test show present',
      long_description='Some more info',
      poster=File(open('test/test_poster.jpg')),
      start_date=start_date,
      end_date=end_date,
      category=cat
      )

  def tearDown(self):
    self.browser.quit()

  def test_list_view(self):
    browser = self.browser

    browser.get(self.live_server_url + '/list')

    # Check that we have a title
    title_text = browser.find_element_by_xpath('//li[@class="poster"][1]/h3').text
    self.assertEqual(title_text, 'Test Show')


class AuthTest(LiveServerTestCase):

  def setUp(self):
    self.browser = webdriver.Chrome('bin/chromedriver')
    os.environ['RECAPTCHA_TESTING'] = 'True'
    User.objects.create_user(
      username='Jim', 
      email='jim@rash.com', 
      password='correcthorsebatterystaple'
      )

  def tearDown(self):
    self.browser.quit()
    os.environ['RECAPTCHA_TESTING'] = 'False'

  def test_login_correct(self):
    browser = self.browser
    browser.get(self.live_server_url + '/')

    # Test that we've actually got a login page
    self.assertIn('login', browser.current_url)

    username = browser.find_element_by_xpath('//form/div[1]/input')
    username.send_keys('Jim')
    password = browser.find_element_by_xpath('//form/div[2]/input')
    # Send the wrong password
    password.send_keys('correcthorsebatterystapleerror')

    self.browser.execute_script(
      "return jQuery('#g-recaptcha-response').val('PASSED')")

    # Submit the form
    submit = browser.find_element_by_xpath('//button[@type="submit"]')
    submit.click()

    # Incase it takes a little bit to load
    browser.implicitly_wait(3)
    error_text = browser.find_element_by_xpath('//p[@class="red-text"]').text
    # Make sure we got an error
    self.assertIn('incorrect', error_text)

    # Test that we're still on the login page
    self.assertIn('login', browser.current_url)

    username = browser.find_element_by_xpath('//form/div[1]/input')
    username.send_keys('Jim')
    password = browser.find_element_by_xpath('//form/div[2]/input')
    # Send the correct password
    password.send_keys('correcthorsebatterystaple')

    self.browser.execute_script(
      "return jQuery('#g-recaptcha-response').val('PASSED')")

    # Submit the form
    submit = browser.find_element_by_xpath('//button[@type="submit"]')
    submit.click()

    nav_text = browser.find_element_by_xpath('//a[@class="dropdown-button"]').text
    # Check the username is in the nav
    self.assertIn('Jim', nav_text)

    # Test login page with authenticated user
    browser.get(self.live_server_url + '/login/')

    nav_text = browser.find_element_by_xpath('//a[@class="dropdown-button"]').text
    # Check the username is in the nav
    self.assertIn('Jim', nav_text)

    # Test login page with a page request with authenticated user
    browser.get(self.live_server_url + '/login/?Pnext=/')
    
    nav_text = browser.find_element_by_xpath('//a[@class="dropdown-button"]').text
    # Check the username is in the nav
    self.assertIn('Jim', nav_text)

    # test that we can logout as well
    browser.get(self.live_server_url + '/')
    browser.find_element_by_xpath('//ul[@id="dropdown1"]/li[3]/a').click()

    logout = browser.find_element_by_xpath('//h4[@class="light nnt-orange medium-text"]').text
    self.assertEqual(logout, 'Logged Out')


