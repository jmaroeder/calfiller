from datetime import datetime
import dateutil.parser
import csv

from werkzeug.security import generate_password_hash, check_password_hash

from icalendar import Calendar, Event


from calfiller import db


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
    special = db.Column(db.Integer, default=0, nullable=False)
    
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
    special = db.Column(db.Integer, default=0, nullable=False)
    
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
                    period = a['period']
                    if d.special != 0:
                        # special schedule day - find the special schedule
                        alt_period = Period.query.filter_by(school=period.school,
                                                            name=period.name,
                                                            special=d.special).first()
                        if alt_period:
                            period = alt_period
                    
                    event = Event()
                    event.add('summary', a['title'])
                    event.add('dtstart', datetime.combine(d.date, period.start_time))
                    event.add('dtend', datetime.combine(d.date, period.end_time))
                    event.add('location', '') # Location seems to be required by Google
                    cal.add_component(event)
                    added += 1

        return cal.to_ical()


def parse_datetime(s):
    return dateutil.parser.parse(s)


def parse_time(s):
    return dateutil.parser.parse(s).time()


def parse_date(s):
    return dateutil.parser.parse(s).date()




def import_periods(f, school, clear=True):
    if clear:
        Period.query.filter_by(school=school).delete()
    added = 0

    reader = csv.DictReader(f)
    for r in reader:
        db.session.add(Period(name=r['period'],
                              start_time=parse_time(r['start']),
                              end_time=parse_time(r['end']),
                              school=school,
                              special=r.get('special')))
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
        print(r['day_name'])
        letter_day = LetterDay.query.filter_by(school=school, name=r['day_name']).first()
        special = r.get('special')
        db.session.add(DatesDays(date=parse_date(r['date']),
                                 letter_day=letter_day,
                                 school=school,
                                 special=r.get('special')))
        added += 1

    db.session.commit()
    return added


def add_school(name, short_name, password):
    db.session.add(School(name=name, short_name=short_name,
                   password_hash=generate_password_hash(password)))


