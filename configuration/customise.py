# -*- coding: utf-8 -*-

import datetime

ORG_NAME = "New Theatre"
ORG_CONTACT = "boxoffice@newtheatre.org.uk"

DEFAULT_LOCATION = "New Theatre"

DEFAULT_TIME = datetime.time(19, 30)
DEFAULT_TIME_MATINEE = datetime.time(14, 30)

DEFAULT_MAX_SELL = 80
DEFAULT_HOURS_TIL_CLOSE = 2

SIDEBAR_FILTER_PERIOD = datetime.timedelta(weeks=3)

FRINGE_PRICE = [3.00, '£3.00']
CONCESSION_PRICE = [5.00, '£5.00']
MEMBER_PRICE = [4.00, '£4.00']
PUBLIC_PRICE = [8.00, '£8.00']
MATINEE_FRESHERS_PRICE = [2.50, '£2.50']
MATINEE_FRESHERS_NNT_PRICE = [2.00, '£2.00']

FELLOW_PRICE = [0.00, '£0.00']
SEASON_PRICE = [0.00, '£0.00']

SEASON_TICKET_PRICE = [25.00, '£25.00']

CATEGORY_CHOICES = (
	('IN_HOUSE', 'In House'),
	('FRINGE', 'Fringe'),
	('EXTERNAL', 'External'),
	('STUFF', 'StuFF'),
	('STUFF_EVENTS', 'StuFF Events'),
	)
