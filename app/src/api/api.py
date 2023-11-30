"""
Flask Application

This module defines a Flask web application for managing tasks. It includes routes
for rendering HTML templates, handling API requests, and interacting with a database
to perform CRUD operations on tasks.

The application uses Flask for web development, SQLAlchemy for database interaction,
and models from the 'models' module to represent the data structure.

Note:
    Ensure that the required environment variables such as DB_HOST, DB_PORT, and DB_NAME
    are properly configured before running this application.

Example:
    To run the application:
        $ python app.py

Attributes:
    app (Flask): The Flask application instance.
    DB_HOST (str): The database host obtained from environment variables.
    DB_PORT (str): The database port obtained from environment variables.
    DB_NAME (str): The database name obtained from environment variables.

Routes:
    - '/' : Renders the index template.
    - '/tasks' : Handles tasks-related API requests.
        - GET: Retrieve all tasks.
        - POST: Add a new task.
    - '/tasks/add' : Handles the addition of a new task.
        - POST: Add a new task to the database.
    - '/tasks/delete/<int:task_id>' : Handles the deletion of a task.
        - GET: Delete a task based on its ID.

"""
import os
from flask import Flask, jsonify, request, render_template
from models import db, Task

app = Flask(__name__, template_folder='../ui/templates',
            static_folder='../ui/static')

DB_HOST = os.environ.get('DB_HOST', 'postgresql_db')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://user:password@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db.init_app(app)

with app.app_context():
    # db.session.execute(text('DROP TABLE IF EXISTS "user", "task" CASCADE'))
    db.create_all()


@app.route('/')
def index():
    """
    Render the index template.

    Returns:
        str: Rendered HTML for the index page.
    """
    return render_template('index.html')


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Retrieve all tasks.

    Returns:
        tuple: A tuple containing a JSON response with tasks and a status code.
    """
    tasks = Task.query.all()
    return jsonify({'tasks': [{
        'id': task.id,
        'task': task.task,
        'description': task.description
    } for task in tasks]}), 200


@app.route('/tasks/add', methods=['POST'])
def add_task():
    """
    Add a new task.

    Returns:
        tuple: A tuple containing a JSON response with a success message and a status code.
    """
    data = request.get_json()
    print(data)
    new_task = Task(
        task=data['content']['task'],
        userid=data['user'],
        description=data['content']['description']
    )
    db.session.add(new_task)
    db.session.commit()

    tasks = Task.query.all()
    print(tasks)
    return jsonify({'message': 'Task added successfully',
                    'tasks': [{'id': task.id,
                               'task': task.task,
                               'description': task.description}
                              for task in tasks]}), 200


@app.route('/tasks/delete/<int:task_id>', methods=['GET', 'POST'])
def delete_task(task_id):
    """
    Delete a task.

    Args:
        task_id (int): The ID of the task to be deleted.

    Returns:
        tuple: A tuple containing a JSON response with a success message and a status code.
    """
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully.'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
