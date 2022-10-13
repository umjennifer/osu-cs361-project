from unicodedata import name
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

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


@app.route('/', methods=['GET'])
def index():
    objectives = Objective.query.order_by(Objective.id).all()
    return render_template('index.html', objectives=objectives)

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

#TODO: update for key result
# TODO: update for tasks


if __name__ == "__main__":
    app.run(debug=True)
    # with app.app_context():
    #     db.create_all()
    # pass


# to create a new db
# from app import app
# from app import db
# with app.app_context():
#     db.create_all()


# from app import app,db,Objective,Key_Result
# with app.app_context():
#     kr1 = Key_Result(content='kr1', objective_id=1)
#     kr2 = Key_Result(content='kr2', objective_id=1)
#     kr3 = Key_Result(content='kr3', objective_id=1)
#     db.session.add(kr1)
#     db.session.add(kr2)
#     db.session.add(kr3)
#     db.session.commit()

# from app import app,db,Objective,Key_Result
# with app.app_context():
#     db.select([Key])