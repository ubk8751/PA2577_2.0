"""
Flask User Management and Task Application

This module defines a Flask web application that integrates user management and task
functionality. It uses Flask for web development, Flask-Login for user authentication,
and interacts with user management and task API services.

The application includes routes for rendering HTML templates, handling login/logout,
user registration, and task management. It communicates with the User Management
service (UM) and the Flask API service to perform user-related and task-related
operations, respectively.

Note:
    Ensure that the required environment variables such as DB_HOST, DB_PORT, and DB_NAME
    are properly configured before running this application.

Example:
    To run the application:
        $ python app.py

Attributes:
    app (Flask): The Flask application instance.
    UM_URL (str): The base URL for the User Management service.
    API_URL (str): The base URL for the Flask API service.

Routes:
    - '/' : Renders the index template.
    - '/login' : Handles login functionality.
    - '/register' : Handles user registration.
    - '/tasks' : Displays user tasks.
    - '/tasks/add' : Adds a new task.
    - '/tasks/delete/<int:task_id>' : Deletes a task.

"""
import os
from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_login import LoginManager
import requests


app = Flask(__name__, template_folder='ui/templates',
            static_folder='ui/static')
app.config['SECRET_KEY'] = os.urandom(24)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the user management service using the user ID.

    Args:
        user_id (int): The ID of the user to load.

    Returns:
        User: The loaded user object or None if not found.
    """
    response = requests.get(f'{UM_URL}/users/{user_id}', timeout=5)
    if response.status_code == 200:
        user_data = response.json()
        return user_data
    return None


UM_SERVICE_NAME = 'user_management-service'
UM_PORT = 5001

if os.path.isfile("/var/run/secrets/kubernetes.io/serviceaccount/token"):
    UM_IP = os.environ.get("KUBERNETES_SERVICE_HOST")
else:
    UM_IP = os.environ.get('UM_HOST')

UM_URL = f'http://{UM_IP}:{UM_PORT}'

API_SERVICE_NAME = 'flask-api-service'
API_PORT = 5002

# Check if running inside a Kubernetes cluster
if os.path.isfile("/var/run/secrets/kubernetes.io/serviceaccount/token"):
    API_IP = os.environ.get("KUBERNETES_SERVICE_HOST")
else:
    API_IP = os.environ.get('API_HOST')

API_URL = f'http://{API_IP}:{API_PORT}'


@app.route('/')
def index():
    """
    Render the index template.

    Returns:
        str: Rendered HTML for the index page.
    """
    if 'user_id' not in session:
        flash('Please log in.')
        return render_template('login.html')
    response_tasks = requests.get(f'{API_URL}/tasks', timeout=5)
    if response_tasks.status_code == 200:
        tasks = response_tasks.json().get('tasks', []) if response_tasks.status_code == 200 else []
        return render_template('index.html', tasks=tasks)
    return render_template('index.html', tasks=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle login functionality.

    Returns:
        str: Rendered HTML for the login page or redirects to the index page.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        response = requests.post(
            f'{UM_URL}/login',
            json={'username': username,
                  'password': password},
            timeout=5)
        if response.status_code == 200:
            session['user_id'] = response.json().get('user_id')
            flash('Login successful.')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
        return render_template('login.html')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.

    Returns:
        str: Rendered HTML for the registration page or redirects to the login page.
    """
    if request.method == 'POST':
        # Handle the registration logic here
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        response = requests.post(
            f'{UM_URL}/register',
            json={'username': username, 'password': password, 'email': email},
            timeout=5)
        if response.status_code == 200:
            flash('User added successfully.')
            return redirect(url_for('login'))
        flash('Failed to add user.')

    return render_template('register.html')

@app.route('/tasks/add', methods=['POST'])
def add_task():
    """
    Add a new task.

    Returns:
        str: Rendered HTML for the index page with updated tasks.
    """
    user_id = session.get('user_id')

    if user_id is None:
        flash('Please log in to add a task.')
        return redirect(url_for('login'))

    content = {
        'task': request.form['task'],
        'description': request.form['description']
    }

    data = {'user': user_id, 'content': content}
    response = requests.post(f'{API_URL}/tasks/add', json=data, timeout=5)

    if response.status_code == 200:
        flash('Task added successfully.')
        return redirect(url_for('index'))
    flash('Failed to add the task.')
    return redirect(url_for('index'))

@app.route('/tasks/delete/<int:task_id>', methods=['GET', 'POST'])
def delete_task(task_id):
    """
    Delete a task.

    Returns:
        str: Redirects to the index page.
    """
    user_id = session.get('user_id')
    
    if user_id is None:
        flash('Please log in to add a task.')
        return redirect(url_for('login'))
    
    response = requests.post(f'{API_URL}/tasks/delete/{task_id}', timeout=5)
    if response.status_code == 200:
        flash('Task removed successfully.')
    else:
        flash('Failed to remove the task.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
