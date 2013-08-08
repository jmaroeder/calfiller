
import re

from flask import request, session, g, redirect, url_for, \
    render_template, flash, make_response, send_from_directory, abort

import io

from calfiller import app
from calfiller.models import *



@app.route('/')
def list_schools():
    schools = School.query.order_by(School.name.asc()).all()
    return render_template('list_schools.html', schools=schools)


@app.route('/<school_name>', methods=['GET', 'POST'])
def cal_table(school_name):
    g.school = School.query.filter_by(short_name=school_name).first_or_404()
    session['school_id'] = g.school.id
    g.sched = Schedule(periods=Period.query.filter_by(school=g.school,special=0).
                               order_by(Period.start_time.asc(), Period.end_time.asc()).all(),
                       letter_days=LetterDay.query.filter_by(school=g.school).
                                   order_by(LetterDay.display_order.asc()).all())
    
    if request.method == 'POST':
        g.sched.dates_days = DatesDays.query.filter_by(school=g.school)
        
        # process form fields
        r = re.compile(r'sched_(\d+)_(\d+)')
        for key, value in request.form.iteritems():
            res = r.match(key)
            value = value.strip()
            if res and value:
                start_time = request.form.get('start_{}_{}'.format(res.group(1), res.group(2)))
                end_time = request.form.get('end_{}_{}'.format(res.group(1), res.group(2)))
                if start_time and end_time:
                    # custom time
                    period = Period(start_time=parse_time(start_time),
                                    end_time=parse_time(end_time),
                                    school=g.school)
                else:
                    # predefined time
                    period = Period.query.get_or_404(int(res.group(2)))
                    if period.school != g.school:
                        abort(404)
                g.sched.add(letter_day=LetterDay.query.get_or_404(int(res.group(1))),
                            period=period,
                            title=value)
        
        response = make_response(g.sched.to_ical())
        response.headers['Content-Disposition'] = 'attachment; filename=schedule.ics'
        
        return response
        
    else:
        return render_template('sched_grid.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = School.query.filter_by(short_name=request.form['username']).first()

        if u and u.check_password(request.form['password']):
            session['admin_logged_in'] = True
            session['school_id'] = u.id
            flash('Logged in as {}'.format(u.name))
            return redirect(url_for('admin'))
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out.')
    return redirect(url_for('login'))



@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    error = None

    g.school = School.query.get_or_404(session['school_id'])

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file:
            stream = io.StringIO(unicode(uploaded_file.read()), newline=None)
            if request.form['action'] == 'upload_periods':
                added = import_periods(stream, g.school)
                flash('Imported {} periods.'.format(added))
            elif request.form['action'] == 'upload_letter_days':
                added = import_letter_days(stream, g.school)
                flash('Imported {} day names.'.format(added))
            elif request.form['action'] == 'upload_dates_days':
                added = import_dates_days(stream, g.school)
                flash('Imported {} dates.'.format(added))
            else:
                error = 'Unknown action'
        elif request.form['action'] == 'change_password':
            if g.school.check_password(request.form['old_password']):
                if request.form['new_password1'] == request.form['new_password2']:
                    if request.form['new_password1'].strip() != '':
                        g.school.change_password(request.form['new_password1'])
                        db.session.commit()
                        flash('Password successfuly changed.')
                    else:
                        error = 'Passwords cannot be blank!'
                else:
                    error = 'Passwords do not match!'
            else:
                error = 'Incorrect old password!'
        else:
            error = 'Unknown error'

    periods = Period.query.filter_by(school=g.school).all()
    day_names = LetterDay.query.filter_by(school=g.school).all()
    dates = DatesDays.query.filter_by(school=g.school).limit(10).all()
    return render_template('admin.html', error=error,
                           day_names=day_names, dates=dates, periods=periods)




@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.template_filter('time')
def _jinja2_filter_time(t, fmt=None):
    format = '%I:%M%p'
    return t.strftime(format) 
