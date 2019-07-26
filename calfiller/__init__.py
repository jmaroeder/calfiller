# encoding: utf-8
"""
CalFiller

Created by James Allen on 2013-07-30.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create app
app = Flask(__name__)
app.config.from_pyfile('config.py')

if os.environ.get('CALFILLER_EXTRA_CONFIG'):
    app.config.from_pyfile('config.{}.py'.format(os.environ.get('CALFILLER_EXTRA_CONFIG')))

db = SQLAlchemy(app)

import calfiller.views
