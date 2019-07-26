from calfiller import *
from calfiller.models import *
from werkzeug.security import generate_password_hash, check_password_hash

db.init_app(app)
with app.test_request_context():
	db.drop_all()
	db.create_all()


db.session.add(School(name='Hathaway Brown Upper School', short_name='hbus', password_hash=generate_password_hash('brown')))
db.session.add(School(name='Hathaway Brown Middle School', short_name='hbms', password_hash=generate_password_hash('brown')))
db.session.add(School(name='Hathaway Brown Primary School', short_name='hbps', password_hash=generate_password_hash('brown')))
db.session.commit()

def load_sample_data():
    school = School.query.filter_by(short_name='hbus').first()
    # upload periods
    with open('periods_us.csv', 'rU') as f:
        assert import_periods(f, school)

    # upload day names
    with open('day_names.csv', 'rU') as f:
        assert import_letter_days(f, school)

    # upload dates_days
    with open('dates_days_us.csv', 'rU') as f:
        assert import_dates_days(f, school)


    school = School.query.filter_by(short_name='hbms').first()
    # upload periods
    with open('periods_ms.csv', 'rU') as f:
        assert import_periods(f, school)

    # upload day names
    with open('day_names.csv', 'rU') as f:
        assert import_letter_days(f, school)

    # upload dates_days
    with open('dates_days_ms.csv', 'rU') as f:
        assert import_dates_days(f, school)


    school = School.query.filter_by(short_name='hbps').first()
    # NO periods

    # upload day names
    with open('day_names.csv', 'rU') as f:
        assert import_letter_days(f, school)

    # upload dates_days
    with open('dates_days_us.csv', 'rU') as f:
        assert import_dates_days(f, school)


load_sample_data()
