# Jennifer Um
# CS 361
# Fall 2022

from unicodedata import name
from flask import Flask, render_template, request, redirect, flash, g as app_ctx
from flask_sqlalchemy import SQLAlchemy
import time
import datetime
from datetime import date
import requests
import pandas
from pandas.tseries.offsets import DateOffset




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
    key_results = db.relationship('Key_Result', backref='objective', cascade="all, delete-orphan")

    def __repr__(self):
        return '<Task %r>' % self.id

class Key_Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    objective_id = db.Column(db.Integer, db.ForeignKey('objective.id'))  
    tasks = db.relationship('Task', backref='key_result', cascade="all, delete-orphan")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    recurring = db.Column(db.Boolean, default=False, nullable=False)
    cadence = db.Column(db.String(200), nullable=True)
    startdate = db.Column(db.DateTime, nullable=True)
    enddate = db.Column(db.DateTime, nullable=True)
    done = db.Column(db.Boolean, default=False, nullable=False)
    key_result_id = db.Column(db.Integer, db.ForeignKey('key__result.id'))

class Deleted_Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_of_deleted_objective = db.Column(db.Integer)
    content = db.Column(db.String(200), nullable=False)
    key_results = db.relationship('Deleted_Key_Result', backref='objective', cascade="all, delete-orphan")

    def __repr__(self):
        return '<Task %r>' % self.id

class Deleted_Key_Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_of_deleted_key_result = db.Column(db.Integer)
    content = db.Column(db.String(200), nullable=False)
    objective_id = db.Column(db.Integer, db.ForeignKey('deleted__objective.id'))
    tasks = db.relationship('Deleted_Task', backref='key_result', cascade="all, delete-orphan")

class Deleted_Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_of_deleted_task = db.Column(db.Integer)
    content = db.Column(db.String(200), nullable=False)
    key_result_id = db.Column(db.Integer, db.ForeignKey('deleted__key__result.id'))  # TODO: set as can't be null
     # TODO: cascade delete

# https://sureshdsk.dev/flask-decorator-to-measure-time-taken-for-a-request
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
        flash('New feature: You can now use a date picker to add a due date to a task. Read the Changelog for more information and instructions.') # TODO: figure out new feature process
    objectives = Objective.query.order_by(Objective.id).all()

    return render_template('index.html', objectives=objectives, show_tips=show_tips, random_quote=random_quote)

@app.route('/create/key_result', methods=['POST'])
def create_key_result():
    key_result_content = request.form['key_result_content']
    objective_id = int(request.form['objective_id'])
    new_key_result = Key_Result(content=key_result_content,objective_id=objective_id)
    try:
        db.session.add(new_key_result)
        db.session.commit()

        return redirect('/')
    except:
        return 'There was an issue adding your key result'

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
    new_deleted_objective = Deleted_Objective(content=objective_to_delete.content, id_of_deleted_objective=id)
    try:
        db.session.delete(objective_to_delete)
        
        # add the item to the recently deleted
        db.session.add(new_deleted_objective)

        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that objective'

@app.route('/delete/key_result/<int:id>')
def delete_key_result(id):
    key_result_to_delete = Key_Result.query.get_or_404(id)
    new_deleted_key_result = Deleted_Key_Result(content=key_result_to_delete.content, id_of_deleted_key_result=id, objective_id=key_result_to_delete.objective_id)
    try:
        db.session.delete(key_result_to_delete)
        db.session.add(new_deleted_key_result)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that key result'

@app.route('/delete/task/<int:id>')
def delete_task(id):
    task_to_delete = Task.query.get_or_404(id)
    new_deleted_task = Deleted_Task(content=task_to_delete.content, id_of_deleted_task=id, key_result_id=task_to_delete.key_result_id)
    try:
        db.session.delete(task_to_delete)
        db.session.add(new_deleted_task)
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
    is_recurring = request.form['is_recurring']
    if is_recurring == "false":
        task.startdate = string_to_datetime(request.form['one_time_date'])
        task.enddate = string_to_datetime(request.form['one_time_date'])
        task.recurring = False
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
        create_events(id, start_date, end_date, cadence)
        try:
            db.session.commit()
        except:
            return 'there was an issue updating your task'
        
    return redirect('/')

def string_to_datetime(date_str):
    format = "%Y-%m-%d"
    d = datetime.datetime.strptime(date_str, format)
    return d.date()

def create_events(task_id, start_date, end_date, cadence):
    print("cadence={}".format(cadence))
    if cadence == "daily":
        daily_events_metadata = pandas.date_range(start_date,end_date)
        daily_events = [i.strftime('%Y-%m-%d') for i in daily_events_metadata]
        print("daily_events={}".format(daily_events))
    elif cadence == "weekly":
        weekly_events_metadata = pandas.date_range(start_date,end_date, freq='W')
        weekly_events = [i.strftime('%Y-%m-%d') for i in weekly_events_metadata]
        print("weekly_events={}".format(weekly_events))
    elif cadence == "monthly":
        weekly_events_metadata = pandas.date_range(start_date,end_date, freq='W')
        weekly_events = [i.strftime('%Y-%m-%d') for i in weekly_events_metadata]
        print("weekly_events={}".format(weekly_events))


@app.route('/changelog', methods=['GET'])
def changelog():
    return render_template('changelog.html')

@app.route('/example', methods=['GET'])
def example():
    return render_template('example.html')

@app.route('/instructions', methods=['GET'])
def instructions():
    return render_template('instructions.html')

@app.route('/recently-deleted', methods=['GET'])
def recently_deleted():
    deleted_objectives = Deleted_Objective.query.order_by(Deleted_Objective.id).all()
    deleted_key_results = Deleted_Key_Result.query.order_by(Deleted_Key_Result.id).all()
    deleted_tasks = Deleted_Task.query.order_by(Deleted_Task.id).all()
    return render_template('recently-deleted.html', deleted_objectives=deleted_objectives, deleted_key_results=deleted_key_results, deleted_tasks=deleted_tasks)

# @app.teardown_request
# def teardown_request(exception=None):
#     diff = time.time() - g.start
#     print("diff=", diff)


#TODO: update for key result
# TODO: update for tasks


if __name__ == "__main__":
    app.run(debug=True)

# to create a new db
# from app import app
# from app import db
# with app.app_context():
#     db.create_all()