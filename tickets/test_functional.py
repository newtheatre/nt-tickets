from django.test import LiveServerTestCase
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from django.core.files import File
from tickets.models import *

import datetime


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
    self.browser.get(self.live_server_url + '/book/' + str(show_id))

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
    show_id = Show.objects.get(name='Test Show').id
    self.browser.get(self.live_server_url + '/book/' + str(show_id))

    # Input correct details but no date or seats
    name = self.browser.find_element_by_id('id_person_name')
    name.send_keys('Test Name1')
    email = self.browser.find_element_by_id('id_email_address')
    email.send_keys('test@test.com')

    # Submit the form
    self.browser.find_element_by_id('submit-btn').click()
    # Wait a little bit
    # self.browser.implicitly_wait(10)
    occurrence_err = self.browser.find_element_by_xpath(
      '//form[@class="submit-once"]/div[@class="col col_left"]/div[@class="control-group error required"][1]/div[@class="controls"]/p[@class="help-block"]'
      ).text
    self.assertEqual(occurrence_err, 'This field is required.')


# class LoginTest(LiveServerTestCase):

