import os
import unittest
import io
import re

# Enable testing config before importing calfiller
os.environ['CALFILLER_EXTRA_CONFIG'] = 'testing'


from calfiller import app, db
from calfiller.models import *


class CalfillerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        db.create_all()
        self.load_test_data()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        pass
    
    def load_test_data(self):
        db.session.add(School(name='Test School 1', short_name='ts1', password_hash=generate_password_hash('test1')))
        db.session.add(School(name='Test School 2 (Special Schedules)', short_name='ts2', password_hash=generate_password_hash('test2')))
        db.session.add(School(name='Test School 3 (No periods)', short_name='ts3', password_hash=generate_password_hash('test3')))
        db.session.commit()
    
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)
    
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    
    def test_login_logout(self):
        rv = self.login('ts1', 'test1')
        assert 'Logged in as Test School 1' in rv.data
        
        rv = self.logout()
        assert 'Logged out' in rv.data
        
        rv = self.login('ts1x', 'test1')
        assert 'Invalid username/password' in rv.data
        
        rv = self.login('ts1', 'test1x')
        assert 'Invalid username/password' in rv.data
        
    
    def load_sample_data(self):
        school = School.query.filter_by(short_name='ts1').first()
        # upload periods
        with open('periods_us.csv', 'rU') as f:
            assert import_periods(f, school) == 10
        
        # upload day names
        with open('day_names.csv', 'rU') as f:
            assert import_letter_days(f, school) == 6
        
        # upload dates_days
        with open('dates_days_us.csv', 'rU') as f:
            assert import_dates_days(f, school) == 165
        
        
        school = School.query.filter_by(short_name='ts2').first()
        # upload periods
        with open('periods_ms.csv', 'rU') as f:
            assert import_periods(f, school) == 20
        
        # upload day names
        with open('day_names.csv', 'rU') as f:
            assert import_letter_days(f, school) == 6
        
        # upload dates_days
        with open('dates_days_ms.csv', 'rU') as f:
            assert import_dates_days(f, school) == 164
        

        school = School.query.filter_by(short_name='ts3').first()
        # NO periods

        # upload day names
        with open('day_names.csv', 'rU') as f:
            assert import_letter_days(f, school) == 6

        # upload dates_days
        with open('dates_days_us.csv', 'rU') as f:
            assert import_dates_days(f, school) == 165
        
    
    def test_importers(self):
        self.load_sample_data()
    
    
    def test_ts1(self):
        self.load_sample_data()
        
        school = School.query.filter_by(short_name='ts1').first()
        
        rv = self.app.get('/ts1')
        assert 'Test School 1' in rv.data
        
        begin_vevent = re.compile(r'BEGIN:VEVENT')
        
        # test each letter day/period combo
        for letter_day in LetterDay.query.filter_by(school=school).all():
            for period in Period.query.filter_by(school=school).all():
                field_name = 'sched_{}_{}'.format(letter_day.id, period.id)
                appt_summary = '{}:{}'.format(letter_day.name, period.name)
                rv = self.app.post('/ts1', data={
                    field_name: appt_summary
                })
                res = begin_vevent.findall(rv.get_data())
                # test number of events added
                assert len(res) == len(DatesDays.query.filter_by(school=school, letter_day=letter_day).all())
                
        
        
if __name__ == '__main__':
    unittest.main()
    
    # close out db fd/delete file
    os.close(app.config['DB_FD'])
    os.unlink(app.config['DB_FILENAME'])