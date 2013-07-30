#!/usr/bin/env python
# encoding: utf-8
"""
fill.py

Created by James Allen on 2013-07-29.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from icalendar import Calendar, Event
from datetime import datetime, date, time
import pytz

class Schedule(object):
	"""docstring for Schedule"""
	def __init__(self, periods, letter_days, dates_days):
		super(Schedule, self).__init__()
		
		self.periods = periods # dict of period => (start_time, end_time)
		
		self.letter_days = letter_days
		
		self.dates_days = dates_days # list of tuples of (date, letter_day)
		
		self.appts = [] # list of tuple of (letter_day, period, title, loc)
		
	def add(self, period, letter_day, title, loc = None):
		if loc is None:
			loc = ''
		
		self.appts.add( (letter_day, period, title, loc) )

	def to_ical():
		cal = Calendar()
		for a in self.appts:
			letter_day, period, title, loc = a
			
			start_time, end_time = self.periods[period]
			
			for d in self.dates_days:
				if d[1] == letter_day:
					event = Event()
					event.add('summary', title)
					if not loc is None:
						event.add('location', loc)
					event.add('dtstart', datetime.combine(d[0], start_time))
					event.add('dtend', datetime.combine(d[0], end_time))


def main():
	pass


if __name__ == '__main__':
	main()

