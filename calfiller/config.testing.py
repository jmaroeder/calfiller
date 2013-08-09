import tempfile

DB_FD, DB_FILENAME = tempfile.mkstemp()

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_FILENAME
DATABASE_CONNECT_OPTIONS = {}
TESTING = True