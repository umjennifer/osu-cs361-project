from unicodedata import name
from flask import Flask, render_template, request, redirect, flash, g as app_ctx
from flask_sqlalchemy import SQLAlchemy
import time
from datetime import date


new_feature = True
show_tips = False

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///okr.db'
db = SQLAlchemy(app)

# TODO: create objects for objectives, key results, tasks?
class Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    key_results = db.relationship('Key_Result', backref='objective', cascade="all, delete-orphan")

    def __repr__(self):
        return '<Task %r>' % self.id

class Key_Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    objective_id = db.Column(db.Integer, db.ForeignKey('objective.id'))  # TODO: set as can't be null
    tasks = db.relationship('Task', backref='key_result', cascade="all, delete-orphan")
     # TODO: cascade this delete

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    key_result_id = db.Column(db.Integer, db.ForeignKey('key__result.id'))  # TODO: set as can't be null
     # TODO: cascade delete

class Deleted_Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    key_results = db.relationship('Deleted_Key_Result', backref='objective', cascade="all, delete-orphan")

    def __repr__(self):
        return '<Task %r>' % self.id

class Deleted_Key_Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    objective_id = db.Column(db.Integer, db.ForeignKey('deleted__objective.id'))  # TODO: set as can't be null
    tasks = db.relationship('Deleted_Task', backref='key_result', cascade="all, delete-orphan")
     # TODO: cascade this delete

class Deleted_Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

    if new_feature is True:
        flash('New feature: You can now use a date picker to add a due date to a task. Read the Changelog for more information and instructions.') # TODO: figure out new feature process
    objectives = Objective.query.order_by(Objective.id).all()

    return render_template('index.html', objectives=objectives, show_tips=show_tips)

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
    try:
        db.session.delete(objective_to_delete)
        print("objective_to_delete=", objective_to_delete)

        # add the item to the recently deleted
        

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
def update(id):
    objective = Objective.query.get_or_404(id)
    if request.method == 'POST':
        objective.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'there was an issue updating your objective'
    else:
        return render_template('update.html', objective=objective)


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
    return render_template('recently-deleted.html')

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