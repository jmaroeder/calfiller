# encoding: utf-8
"""
CalFiller

Created by James Allen on 2013-07-30.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# create app
app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

import calfiller.views

def create_app():
    db.init_app(app)