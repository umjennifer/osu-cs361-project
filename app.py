from unicodedata import name
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# TODO: create objects for objectives, key results, tasks?
class Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    key_results = db.relationship('Key_Result', backref='objective')

    def __repr__(self):
        return '<Task %r>' % self.id

class Key_Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    objective_id = db.Column(db.Integer, db.ForeignKey('objective.id'))

@app.route('/', methods=['POST'])
def create():
    print("request.form=", request.form)  # TODO: delete
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
    # if request.method == 'POST':
    #     objective_content = request.form['content']
    #     new_objective = Objective(content=objective_content)

    #     try:
    #         db.session.add(new_objective)
    #         db.session.commit()
    #         return redirect('/')
    #     except:
    #         return 'There was an issue adding your objective'

    # else:
        objectives = Objective.query.order_by(Objective.id).all()
        return render_template('index.html', objectives=objectives)

@app.route('/delete/objective/<int:id>')
def delete(id):
    objective_to_delete = Objective.query.get_or_404(id)
    try:
        db.session.delete(objective_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that objective'

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

if __name__ == "__main__":
    app.run(debug=True)
    # with app.app_context():
    #     db.create_all()
    # pass


# # to create a new db
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