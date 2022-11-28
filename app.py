# Jennifer Um
# CS 361
# Fall 2022

from unicodedata import name
from flask import Flask, render_template, request, redirect, flash, g as app_ctx
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
import time
import datetime
from datetime import date, timedelta
import requests
import pandas
from pandas.tseries.offsets import DateOffset
import calendar

new_feature = False
show_tips = False
quoteservice = 'http://127.0.0.1:3000/'

def get_random_quote():
    response = requests.get(quoteservice, timeout=10)
    return response.text

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///okr.db'
db = SQLAlchemy(app)

class Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(), nullable=True)
    done = db.Column(db.Boolean, default=False, nullable=False)
    key_results = db.relationship('Key_Result', backref='objective', cascade="all, delete-orphan")
    event = db.relationship('Event', backref='objective', cascade="all, delete-orphan")
    count_total_events = db.Column(db.Integer, default=0)
    count_events_not_done = db.Column(db.Integer, default=0)

class Key_Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    objective_id = db.Column(db.Integer, db.ForeignKey('objective.id'))
    done = db.Column(db.Boolean, default=False, nullable=False)  
    tasks = db.relationship('Task', backref='key_result', cascade="all, delete-orphan")
    event = db.relationship('Event', backref='key_result', cascade="all, delete-orphan")
    count_total_events = db.Column(db.Integer, default=0)
    count_events_not_done = db.Column(db.Integer, default=0)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    recurring = db.Column(db.Boolean, default=False, nullable=False)
    cadence = db.Column(db.String(200), nullable=True)
    startdate = db.Column(db.Date, nullable=True)
    enddate = db.Column(db.Date, nullable=True)
    done = db.Column(db.Boolean, default=False, nullable=False)
    key_result_id = db.Column(db.Integer, db.ForeignKey('key__result.id'))
    event = db.relationship('Event', backref='task', cascade="all, delete-orphan")
    count_total_events = db.Column(db.Integer, default=0)
    count_events_not_done = db.Column(db.Integer, default=0)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    key_result_id = db.Column(db.Integer, db.ForeignKey('key__result.id'), nullable=False)
    objective_id = db.Column(db.Integer, db.ForeignKey('objective.id'), nullable=False)

# Citation: https://sureshdsk.dev/flask-decorator-to-measure-time-taken-for-a-request
@app.before_request
def logging_before():
    # Store the start time for the request
    app_ctx.start_time = time.perf_counter()
@app.after_request
def logging_after(response):
    # Get total time in milliseconds
    total_time = time.perf_counter() - app_ctx.start_time
    # Log the time taken for the endpoint 
    write_to_log=('{} s, {}, {}, {}\n'.format(total_time, date.today(), request.method, request.path))
    f = open("responsiveness.log", "a")
    f.write(write_to_log)
    f.close()
    return response   

@app.route('/', methods=['GET'])
def index():
    random_quote = get_random_quote()
    if new_feature is True:
        flash('New feature: You can now click "Today\'s Task" in the navigation bar to view your tasks for the day.') 
    objectives = Objective.query.order_by(Objective.id).all()
    events = Event.query.order_by(Event.task_id).all()
    return render_template(
        'index.html', 
        objectives=objectives, 
        events=events,
        show_tips=show_tips, 
        random_quote=random_quote, 
        today=date.today())

@app.route('/select-date', methods=['POST'])
def select_date():
    selected_date = request.form['selected_date']
    return redirect('/tasks/date/' + selected_date)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/tasks/date/today', methods=['GET'])
def select_today():
    return redirect('/tasks/date/' + str(date.today()))

@app.route('/tasks/date/<desired_date>', methods=['GET'])
def tasks_for_date(desired_date):
    events = db.session.query(Event).filter_by(date=desired_date).all()
    events_tasks_kr_objectives = []
    for event in events:
        task = get_task_from_event(event)
        key_result = get_key_result_from_task(task)
        objective = get_objective_from_key_result(key_result)
        events_tasks_kr_objectives.append((event, task, key_result, objective))
    return render_template(
        'date.html', 
        previous_date = string_to_datetime(desired_date) - timedelta(1),
        next_date = string_to_datetime(desired_date) + timedelta(1),
        events_tasks_kr_objectives=events_tasks_kr_objectives,
        desired_date=desired_date, 
        day_of_week = calendar.day_name[string_to_datetime(desired_date).weekday()])

@app.route('/create/key_result', methods=['POST'])
def create_key_result():
    key_result_content = request.form['key_result_content']
    objective_id = int(request.form['objective_id'])
    new_key_result = Key_Result(content=key_result_content,objective_id=objective_id)
    try:
        db.session.add(new_key_result)
        db.session.commit()
    except:
        return 'There was an issue adding your key result'
    objective = Objective.query.get_or_404(objective_id)
    objective.done = check_if_all_key_results_for_objective_are_done(objective)
    try:
        db.session.commit()
    except:
        return 'There was an issue updating done status of objective'
    return redirect('/')

@app.route('/create/task', methods=['POST'])
def create_task():
    task_content = request.form['task_content']
    key_result_id = int(request.form['key_result_id'])
    new_task = Task(content=task_content,key_result_id=key_result_id)
    try:
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue adding your task'

@app.route('/create/objective', methods=['POST'])
def create_objective():
    objective_content = request.form['objective_content']
    new_objective = Objective(content=objective_content)
    try:
        db.session.add(new_objective)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue adding your objective'

@app.route('/tips/show', methods=['POST'])
def tips_show():
    tips_visibility = request.form['tips_show']
    objectives = Objective.query.order_by(Objective.id).all()
    if tips_visibility == "true":
        show_tips = True
    return render_template('index.html', objectives=objectives, show_tips=show_tips)

@app.route('/tips/hide', methods=['POST'])
def tips_hide():
    tips_visibility = request.form['tips_hide']
    objectives = Objective.query.order_by(Objective.id).all()
    if tips_visibility == "false":
        show_tips = False
    return render_template('index.html', objectives=objectives, show_tips=show_tips)

@app.route('/delete/objective/<int:id>')
def delete_objective(id):
    objective_to_delete = Objective.query.get_or_404(id)
    try:
        db.session.delete(objective_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that objective'

@app.route('/delete/key_result/<int:id>')
def delete_key_result(id):
    key_result_to_delete = Key_Result.query.get_or_404(id)
    try:
        db.session.delete(key_result_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that key result'

@app.route('/delete/task/<int:id>')
def delete_task(id):
    task_to_delete = Task.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/objective/<int:id>', methods=['GET','POST'])
def update_objective(id):
    objective = Objective.query.get_or_404(id)
    if request.method == 'POST':
        objective.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'there was an issue updating your objective'
    else:
        return render_template('update_objective.html', objective=objective)

@app.route('/update/key_result/<int:id>', methods=['GET','POST'])
def update_key_result(id):
    key_result = Key_Result.query.get_or_404(id)
    if request.method == 'POST':
        key_result.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'there was an issue updating your key result'
    else:
        return render_template('update_key_result.html', key_result=key_result)

@app.route('/update/task/<int:id>', methods=['GET','POST'])
def update_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'there was an issue updating your task'
    else:
        return render_template('update_task.html', task=task, today=date.today())

@app.route('/task/<int:id>/recurrence', methods=['POST'])
def set_task_recurrence(id):
    task = Task.query.get_or_404(id)
    delete_events(id)
    is_recurring = request.form['is_recurring']
    if is_recurring == "false":
        task.startdate = string_to_datetime(request.form['one_time_date'])
        task.enddate = string_to_datetime(request.form['one_time_date'])
        task.recurring = False
        add_event_to_table(id, request.form['one_time_date'])
        try:
            db.session.commit()
        except:
            return 'there was an issue updating your task'
    else:  # is_recurring == "true"
        cadence = request.form['recurrence_cadence']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        if end_date < start_date:
            flash('Error: Select an end date after the start end.')
            task = Task.query.get_or_404(id)
            return render_template('update_task.html', task=task, today=date.today())
        task.startdate = string_to_datetime(start_date)
        task.enddate = string_to_datetime(end_date)
        task.recurring = True
        task.cadence = cadence
        events = get_event_dates(id, start_date, end_date, cadence)
        add_events_to_table(id, events)
        try:
            db.session.commit()
        except:
            return 'there was an issue updating your task'
    return redirect('/')

def delete_events(task_id):
    for event in db.session.query(Event).filter_by(task_id=task_id):
        try:
            db.session.delete(event)
            db.session.commit()
        except:
            return 'There was an issue deleting previous event(s) associated with task'

def add_events_to_table(task_id, events):
    for event in events:
        add_event_to_table(task_id, event)

def add_event_to_table(task_id, event_date_string):
    event_date = string_to_datetime(event_date_string)
    task = Task.query.get_or_404(task_id)
    key_result = get_key_result_from_task(task)
    objective = get_objective_from_key_result(key_result)
    new_event = Event(date=event_date, task_id=task_id, objective_id=objective.id, key_result_id=key_result.id)
    try:
        db.session.add(new_event)
        db.session.commit()
    except:
        return 'There was an issue adding an event on the day specified'
    update_done_status_of_task(task)
    update_done_status_of_key_result(key_result)
    update_done_status_of_objective(objective)

def string_to_datetime(date_str):
    format = "%Y-%m-%d"
    d = datetime.datetime.strptime(date_str, format)
    return d.date()

def get_event_dates(task_id, start_date, end_date, cadence):
    if cadence == "daily":
        daily_events_metadata = pandas.date_range(start_date,end_date)
        return [i.strftime('%Y-%m-%d') for i in daily_events_metadata]
    elif cadence == "weekly":
        weekly_events_metadata = pandas.date_range(start_date,end_date, freq='W')
        return [i.strftime('%Y-%m-%d') for i in weekly_events_metadata]
    elif cadence == "monthly":
        monthly_events_metadata = month_range_day(start_date, num_months_between_two_dates(start_date, end_date))
        return [i.strftime('%Y-%m-%d') for i in monthly_events_metadata]
    else:  # cadence == "yearly"
        yearly_events_metadata = pandas.date_range(
            start=start_date, 
            periods=(
                (num_months_between_two_dates(start_date, end_date) // 12) + 1), 
            freq=pandas.DateOffset(years=1)
            )
        return [i.strftime('%Y-%m-%d') for i in yearly_events_metadata]

# Citation: https://stackoverflow.com/a/4040338 
def num_months_between_two_dates(date1, date2):
    date1 = string_to_datetime(date1)
    date2 = string_to_datetime(date2)
    return abs((date1.year - date2.year) * 12 + date1.month - date2.month) + 1 # add one to include date

# Citation: https://stackoverflow.com/a/51881983
def month_range_day(start, periods):
    start_date = pandas.Timestamp(start).date()
    month_range = pandas.date_range(start=start_date, periods=periods, freq='M')
    month_day = month_range.day.values
    month_day[start_date.day < month_day] = start_date.day
    return pandas.to_datetime(month_range.year*10000+month_range.month*100+month_day, format='%Y%m%d')

@app.route('/changelog', methods=['GET'])
def changelog():
    return render_template('changelog.html')

@app.route('/example', methods=['GET'])
def example():
    return render_template('example.html')

@app.route('/instructions', methods=['GET'])
def instructions():
    return render_template('instructions.html')

@app.route('/task/done', methods=['POST'])
def mark_task_as_done():
    task = Task.query.get_or_404(request.form['task_id']) 
    event = Event.query.get_or_404(request.form['event_id']) 
    event.done = True
    try:
        db.session.commit()
    except:
        return "error marking the task for the day as done"
    update_done_status_of_task(task)
    key_result = get_key_result_from_task(task)
    update_done_status_of_key_result(key_result)
    objective = get_objective_from_key_result(key_result)
    update_done_status_of_objective(objective)
    return redirect('/tasks/date/'+str(event.date))

@app.route('/task/not-done', methods=['POST'])
def mark_task_as_not_done():
    task = Task.query.get_or_404(request.form['task_id']) 
    event = Event.query.get_or_404(request.form['event_id']) 
    event.done = False
    try:
        db.session.commit()
    except:
        return "error marking the task for the day as done"
    update_done_status_of_task(task)
    key_result = get_key_result_from_task(task)
    update_done_status_of_key_result(key_result)
    objective = get_objective_from_key_result(key_result)
    update_done_status_of_objective(objective)
    return redirect('/tasks/date/'+str(event.date))

def update_done_status_of_objective(objective):
    count_events_not_done = db.session.query(Event).filter_by(done=False, objective_id=objective.id).count()
    count_total_events = db.session.query(Event).filter_by(objective_id=objective.id).count()
    objective.count_events_not_done = count_events_not_done
    objective.count_total_events = count_total_events
    objective.done = check_if_all_key_results_for_objective_are_done(objective)
    try:
        db.session.commit()
    except:
        return "error updating objective done status"

def update_done_status_of_key_result(key_result):
    count_events_not_done = db.session.query(Event).filter_by(done=False, key_result_id=key_result.id).count()
    count_total_events = db.session.query(Event).filter_by(key_result_id=key_result.id).count()
    key_result.count_events_not_done = count_events_not_done
    key_result.count_total_events = count_total_events
    key_result.done = check_if_all_tasks_for_key_results_are_done(key_result)
    try:
        db.session.commit()
    except:
        return "error updating key_result done status"
        
def update_done_status_of_task(task):
    count_events_not_done = db.session.query(Event).filter_by(done=False, task_id=task.id).count()
    count_total_events = db.session.query(Event).filter_by(task_id=task.id).count()
    task.count_events_not_done = count_events_not_done
    task.count_total_events = count_total_events
    task.done = check_if_all_events_for_task_are_done(task)
    try:
        db.session.commit()
    except:
        return "error updating task done status"

def check_if_all_events_for_task_are_done(task):
    not_done_events = db.session.query(Event).filter_by(task_id=task.id, done=False).all()

    if len(not_done_events) > 0:
        return False
    return True

def check_if_all_tasks_for_key_results_are_done(key_result):
    not_done_tasks_for_key_result = db.session.query(Task).filter_by(key_result_id=key_result.id, done=False).all()
    if len(not_done_tasks_for_key_result) > 0:
        return False
    return True

def check_if_all_key_results_for_objective_are_done(objective):
    not_done_key_result_for_objective = db.session.query(Key_Result).filter_by(objective_id=objective.id, done=False).all()
    if len(not_done_key_result_for_objective) > 0:
        return False
    return True

def get_task_from_event(event):
    return db.session.query(Task).filter_by(id=event.task_id).all()[0]

def get_key_result_from_task(task):
    return db.session.query(Key_Result).filter_by(id=task.key_result_id).all()[0]

def get_objective_from_key_result(key_result):
    return db.session.query(Objective).filter_by(id=key_result.objective_id).all()[0]


if __name__ == "__main__":
    app.run(debug=True)

