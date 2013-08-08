from calfiller import *
from calfiller.models import *
from werkzeug.security import generate_password_hash, check_password_hash

db.init_app(app)
with app.test_request_context():
	db.create_all()


db.session.add(School(name='Hathaway Brown Upper School', short_name='hbus', password_hash=generate_password_hash('brown')))
db.session.add(School(name='Hathaway Brown Middle School', short_name='hbms', password_hash=generate_password_hash('brown')))
db.session.add(School(name='Hathaway Brown Primary School', short_name='hbps', password_hash=generate_password_hash('brown')))
db.session.commit()

