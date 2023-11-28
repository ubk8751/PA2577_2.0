from flask import Flask, jsonify, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
import time

from models import db, User

app = Flask(__name__, template_folder='../ui/templates', static_folder='../ui/static')

DB_HOST = os.environ.get('DB_HOST', 'postgresql_db')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://user:password@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db.init_app(app)

with app.app_context():
    #db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.form.to_dict()
    print(data)
    new_user = User(username=data['username'], password=data['password'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return redirect('/users')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)