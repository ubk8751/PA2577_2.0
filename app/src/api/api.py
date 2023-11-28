from flask import Flask, jsonify, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os

from models import db, User, Task

app = Flask(__name__, template_folder='../ui/templates')

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://user:password@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db.init_app(app)

with app.app_context():
    
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)

@app.route('/tasks/add', methods=['POST'])
def add_task():
    data = request.form    
    user = User.query.first()
    print(user)
    if user == None:
        new_user = User(username='John Doe', email='john.doe@test.com')
        db.session.add(new_user)
        db.session.commit()
        flash('No users are registered. Adding default user for testing purposes.')
        return redirect('/tasks')
    elif user:
        new_task = Task(task=data['task'], userid=user.id, description=data['description'])
        db.session.add(new_task)
        db.session.commit()
        return redirect('/tasks')
    else:
        return redirect('/tasks')

@app.route('/tasks/delete/<int:task_id>', methods=['GET', 'POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully.')
    return redirect('/tasks')

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({'username': user.username, 'email': user.email})
    return jsonify({'users': user_list})

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
