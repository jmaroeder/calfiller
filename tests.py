import os
import unittest
import tempfile
import io

from calfiller import app, create_app
from calfiller.models import *



class CalfillerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, self.db_filename = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.db_filename
        app.config['TESTING'] = True
        create_app()
        self.app = app.test_client()
        db.create_all()
        self.load_test_data()
        
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_filename)
    
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
        
    
    def test_admin(self):
        rv = self.login('ts1', 'test1')
        rv = self.app.post()
        
        school = School.query.filter_by(short_name='ts1').first()
        # upload periods
        with open('periods_us.csv') as f:
            assert import_periods(f, school) == 10
        
        # upload day names
        with open('day_names.csv') as f:
            assert import_letter_days(f, school) == 6
        
        # upload dates_days
        with open('dates_days_us.csv') as f:
            assert import_dates_days(f, school) == 165
        
        
        school = School.query.filter_by(short_name='ts2').first()
        # upload periods
        with open('periods_ms.csv') as f:
            assert import_periods(f, school) == 10
        
        # upload day names
        with open('day_names.csv') as f:
            assert import_letter_days(f, school) == 6
        
        # upload dates_days
        with open('dates_days_ms.csv') as f:
            assert import_dates_days(f, school) == 165
        

        school = School.query.filter_by(short_name='ts3').first()
        # NO periods

        # upload day names
        with open('day_names.csv') as f:
            assert import_letter_days(f, school) == 6

        # upload dates_days
        with open('dates_days_us.csv') as f:
            assert import_dates_days(f, school) == 165

        
        
if __name__ == '__main__':
    unittest.main()