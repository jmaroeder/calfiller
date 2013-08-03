# encoding: utf-8
"""
calfiller.py

Created by James Allen on 2013-07-30.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sqlite3

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, make_response, send_from_directory

from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

#from schedule import Schedule

from contextlib import closing

from datetime import datetime
from icalendar import Calendar, Event

import dateutil.parser
import csv
import io, os
import re



# temp hardcoded school_id
SCHOOL_ID = 1



# create app
app = Flask(__name__)
app.config.from_pyfile('calfiller.cfg')


# 
# def adapt_time(t):
#     return t.strftime('%H:%M:%S')
# 
# def convert_time(s):
#     return dateutil.parser.parse(s).time()
# 
# 
# #sqlite3.register_adapter(time, adapt_time)
# #sqlite3.register_converter('time', convert_time)
# 
# 

# Database Model
db = SQLAlchemy(app)

class School(db.Model):
    __tablename__ = 'schools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    short_name = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(160), nullable=False)
    
    def change_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    

class Period(db.Model):
    __tablename__ = 'periods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    school = db.relationship('School', backref=db.backref('periods', lazy='dynamic'))


class LetterDay(db.Model):
    __tablename__ = 'letter_days'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    school = db.relationship('School', backref=db.backref('letter_days', lazy='dynamic'))


class DatesDays(db.Model):
    __tablename__ = 'dates_days'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    
    letter_day_id = db.Column(db.Integer, db.ForeignKey('letter_days.id'), nullable=False)
    letter_day = db.relationship('LetterDay', backref=db.backref('dates_days', lazy='dynamic'))
    
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    school = db.relationship('School', backref=db.backref('dates_days', lazy='dynamic'))
    
    
    
    


class Schedule(object):
    def __init__(self, periods = None, letter_days = None, dates_days = None):
        self.periods = periods
        self.letter_days = letter_days
        self.dates_days = dates_days
        self.appts = [] # list of dicts of (letter_day, period, title)

    def add(self, letter_day, period, title):
        self.appts.append(dict(letter_day=letter_day, period=period, title=title))

    def to_ical(self):
        added = 0
        cal = Calendar()
        for a in self.appts:
            for d in self.dates_days:
                if d.letter_day == a['letter_day']:
                    event = Event()
                    event.add('summary', a['title'])
                    event.add('dtstart', datetime.combine(d.date, a['period'].start_time))
                    event.add('dtend', datetime.combine(d.date, a['period'].end_time))
                    event.add('location', '') # Location seems to be required
                    cal.add_component(event)
                    added += 1

        #flash("Saved {} appointments.".format(added))
        return cal.to_ical()



@app.before_request
def before_request():
    pass
    

@app.teardown_request
def teardown_request(exception):
    pass
    

@app.route('/')
def list_schools():
    return 'TODO'


@app.route('/<school_name>', methods=['GET', 'POST'])
def cal_table(school_name):
    g.school = School.query.filter_by(short_name=school_name).first_or_404()
    session['school_id'] = g.school.id
    g.sched = Schedule(periods=Period.query.filter_by(school=g.school).
                               order_by(Period.start_time.asc(), Period.end_time.asc()).all(),
                       letter_days=LetterDay.query.filter_by(school=g.school).
                                   order_by(LetterDay.display_order.asc()).all())
    
    if request.method == 'POST':
        g.sched.dates_days = DatesDays.query.filter_by(school=g.school)
        
        # process form fields
        r = re.compile(r'sched_(\d+)_(\d+)')
        for key, value in request.form.iteritems():
            res = r.match(key)
            value = value.strip()
            if res and value:
                g.sched.add(letter_day=LetterDay.query.get_or_404(int(res.group(1))),
                            period=Period.query.get_or_404(int(res.group(2))),
                            title=value)
        
        # for i in range(len(g.sched.periods)):
        #     for j in range(len(g.sched.letter_days)):
        #         entry = request.form['sched_{}_{}'.format(i, j)]
        #         if entry:
        #             g.sched.add(g.sched.periods[i], g.sched.letter_days[j], entry)
        
        response = make_response(g.sched.to_ical())
        response.headers['Content-Disposition'] = 'attachment; filename=schedule.ics'
        
        return response
        
    else:
        return render_template('sched_grid.html')


def import_periods(f, school, clear=True):
    if clear:
        Period.query.filter_by(school=school).delete()
    added = 0
    
    reader = csv.DictReader(f)
    for r in reader:
        db.session.add(Period(name=r['period'],
                              start_time=dateutil.parser.parse(r['start']).time(),
                              end_time=dateutil.parser.parse(r['end']).time(),
                              school=school))
        added += 1
    db.session.commit()
    return added


def import_letter_days(f, school, clear=True):
    if clear:
        LetterDay.query.filter_by(school=school).delete()
        DatesDays.query.filter_by(school=school).delete()
    added = 0

    for line in f:
        line = line.strip()
        if line == '':
            pass
        db.session.add(LetterDay(name=line, display_order=added, school=school))
        added += 1
        
    db.session.commit()
    return added


def import_dates_days(f, school, clear=True):
    
    if clear:
        DatesDays.query.filter_by(school=school).delete()
    added = 0

    reader = csv.DictReader(f)
    for r in reader:
        letter_day = LetterDay.query.filter_by(school=school, name=r['day_name']).first()
        db.session.add(DatesDays(date=dateutil.parser.parse(r['date']).date(),
                                 letter_day=letter_day,
                                 school=school))
        added += 1
        
    db.session.commit()
    return added


def add_school(name, short_name, password):
    db.session.add(School(name=name, short_name=short_name,
                   password_hash=generate_password_hash(password)))



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = School.query.filter_by(short_name=request.form['username']).first()
        
        if u and u.check_password(request.form['password']):
            session['admin_logged_in'] = True
            session['school_id'] = u.id
            flash('Logged in as {}'.format(u.name))
            return redirect(url_for('admin'))
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    error = None
    
    g.school = School.query.get_or_404(session['school_id'])
    
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file:
            stream = io.StringIO(unicode(uploaded_file.read()), newline=None)
            if request.form['action'] == 'upload_periods':
                added = import_periods(stream, g.school)
                flash('Imported {} periods.'.format(added))
            elif request.form['action'] == 'upload_letter_days':
                added = import_letter_days(stream, g.school)
                flash('Imported {} day names.'.format(added))
            elif request.form['action'] == 'upload_dates_days':
                added = import_dates_days(stream, g.school)
                flash('Imported {} dates.'.format(added))
            else:
                error = 'Unknown action'
        elif request.form['action'] == 'change_password':
            if g.school.check_password(request.form['old_password']):
                if request.form['new_password1'] == request.form['new_password2']:
                    if request.form['new_password1'].strip() != '':
                        g.school.change_password(request.form['new_password1'])
                        db.session.commit()
                        flash('Password successfuly changed.')
                    else:
                        error = 'Passwords cannot be blank!'
                else:
                    error = 'Passwords do not match!'
            else:
                error = 'Incorrect old password!'
        else:
            error = 'Unknown error'
    
    periods = Period.query.filter_by(school=g.school).all()
    day_names = LetterDay.query.filter_by(school=g.school).all()
    dates = DatesDays.query.filter_by(school=g.school).limit(10).all()
    #assert False
    return render_template('admin.html', error=error,
                           day_names=day_names, dates=dates, periods=periods)

    


@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out.')
    return redirect(url_for('login'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.template_filter('time')
def _jinja2_filter_time(t, fmt=None):
    format = '%I:%M%p'
    return t.strftime(format) 

if __name__ == '__main__':
    app.run()
