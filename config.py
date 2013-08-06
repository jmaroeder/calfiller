# Sample configuration - update this!
# Copy this file to config.py, and edit the values to suit
import os, tempfile

# configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'calfiller.db')
DEBUG = True
SECRET_KEY = '\xa0\x139G~B\xc5ff\xb5\x11\xdf=\xaf\xc7_v\x11^\x88\xd9\x95gS'
