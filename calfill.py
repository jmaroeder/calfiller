# encoding: utf-8
"""
calfill.py

Created by James Allen on 2013-07-30.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sqlite3

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, make_response

from schedule import Schedule

from contextlib import closing

from datetime import time

import dateutil.parser
import csv


# configuration
DATABASE = 'calfill.db'
DEBUG = True
SECRET_KEY = 'devkey'
ADMIN_USER = 'admin'
ADMIN_PASS = 'lanculeceris'

# temp hardcoded school_id
SCHOOL_ID = 1



# create app
app = Flask(__name__)
app.config.from_object(__name__)



def adapt_time(t):
    return t.strftime('%H:%M:%S')

def convert_time(s):
    return dateutil.parser.parse(s).time()


sqlite3.register_adapter(time, adapt_time)
sqlite3.register_converter('time', convert_time)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'],
                           detect_types=sqlite3.PARSE_DECLTYPES)


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def reset():
    init_db()

    # load dates_days
    with closing(connect_db()) as db:
        db.execute('insert into schools (id, name) values (?, ?)',
                   [1, 'Hathaway Brown School']);

        with open('dates_days.csv', 'rU') as f:
            reader = csv.DictReader(f)
            for r in reader:
                db.execute('insert into dates_days (school_id, date, day_name) values (?, ?, ?)',
                           [SCHOOL_ID, dateutil.parser.parse(r['date']).date(), r['day_name']])

        with open('periods.csv', 'rU') as f:
            reader = csv.DictReader(f)
            for r in reader:
                db.execute('insert into periods (school_id, period_name, start_time, end_time) values (?, ?, ?, ?)',
                           [SCHOOL_ID, r['period'],
                            dateutil.parser.parse(r['start']).time(),
                            dateutil.parser.parse(r['end']).time()])

        for letter in 'ABCDEF':
            db.execute('insert into letter_days (school_id, day_name) VALUES (?, ?)',
                       [SCHOOL_ID, letter + ' day'])

        db.commit()



def get_sched(db, school_id = SCHOOL_ID):
    # periods
    cur = db.execute('SELECT period_name, start_time, end_time FROM periods WHERE school_id = ?',
                     [SCHOOL_ID])
    periods = dict()
    for row in cur.fetchall():
        periods[row[0]] = (row[1], row[2])
    
    
    # letter_days
    cur = db.execute('SELECT day_name FROM letter_days WHERE school_id = ? ORDER BY display_order ASC, day_name ASC',
                     [SCHOOL_ID])
    letter_days = [row[0] for row in cur.fetchall()]
    
    
    # dates_days
    cur = db.execute('SELECT date, day_name FROM dates_days WHERE school_id = ?',
                     [SCHOOL_ID])
    dates_days = [(row[0], row[1]) for row in cur.fetchall()]
    
    return Schedule(periods, letter_days, dates_days)



def load_dates():
    pass
    

@app.before_request
def before_request():
    g.db = connect_db()
    g.sched = get_sched(g.db)
    g.sorted_periods = sorted([dict(name=key, start=value[0], end=value[1]) \
                               for key, value in g.sched.periods.iteritems()],
                              key = lambda x: x['start'])
    


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/sched', methods=['GET', 'POST'])
def sched():
    
    if request.method == 'POST':
        # generate ical file (todo)
        print(request.form)
        # process form fields
        for i in range(len(g.sorted_periods)):
            for j in range(len(g.sched.letter_days)):
                entry = request.form['sched_{}_{}'.format(i, j)]
                if entry:
                    print(g.sorted_periods[i]['name'],
                                g.sched.letter_days[j],
                                entry)
                    g.sched.add(g.sorted_periods[i]['name'],
                                g.sched.letter_days[j],
                                entry)
        
        response = make_response(g.sched.to_ical())
        response.headers['Content-Disposition'] = 'attachment; filename=schedule.ics'
        
        return response
        
        
    else:
        #cur = g.db.execute('select ')
        
        boxes = []
        
        
        return render_template('sched_grid.html',
                               letter_days=g.sched.letter_days,
                               periods=g.sorted_periods)


if __name__ == '__main__':
    app.run()
