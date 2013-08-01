# encoding: utf-8
"""
schedule.py

Created by James Allen on 2013-07-29.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from icalendar import Calendar, Event
from datetime import datetime, date, time
import pytz

import csv


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
		
		self.appts.append( (letter_day, period, title, loc) )

	def to_ical(self):
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
					
					cal.add_component(event)
					
		return cal.to_ical()
	
	
def main():
	periods = dict()
	with open('periods.csv', 'rU') as csvfile:
		reader = csv.DictReader(csvfile)
		for r in reader:
			period = r['period']
			start = time(*(map(int, r['start'].split(':'))))
			end = time(*(map(int, r['end'].split(':'))))
			periods[period] = (start, end)
	
	letter_days = 'ABCDEF'
	
	dates_days = []
	with open('dates_days.csv', 'rU') as csvfile:
		reader = csv.DictReader(csvfile)
		for r in reader:
			date_obj = date(*(map(int, r['date'].split('-'))))
			day = r['day_name']
			dates_days.append((date_obj, day))
	
	
	sched = Schedule(periods, letter_days, dates_days)
	
	sched.add('1', 'A', 'early fun', 'aud')
	sched.add('2', 'B', 'midday')
	
	print(sched.to_ical())
	
	with open('test.ics', 'w') as f:
		f.write(sched.to_ical())

if __name__ == '__main__':
	main()

