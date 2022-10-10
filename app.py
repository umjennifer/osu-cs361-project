from unicodedata import name
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/')
def index():
    return render_template('index.html')  # knows to look in template folder

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
