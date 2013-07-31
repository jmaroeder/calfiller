# encoding: utf-8
"""
calfill.py

Created by James Allen on 2013-07-30.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

from flask import Flask

from fill import *

app = Flask(__name__)
app.debug = True


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/sched', methods=['GET', 'POST'])
def sched():
	if request.method == 'POST':
		pass


if __name__ == '__main__':
    app.run()
