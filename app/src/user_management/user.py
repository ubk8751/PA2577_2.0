"""
Flask User Authentication and Registration

This module defines a Flask web application that handles user authentication and registration.
It utilizes Flask for web development, Flask-Login for user authentication, and SQLAlchemy for
database operations. The application communicates with a PostgreSQL database to store user data.

Note:
    Ensure that the required environment variables such as DB_HOST, DB_PORT, and DB_NAME are
    properly configured before running this application.

Example:
    To run the application:
        $ python app.py

Attributes:
    app (Flask): The Flask application instance.
    login_manager (LoginManager): Manages user authentication.
    DB_HOST (str): Database host.
    DB_PORT (str): Database port.
    DB_NAME (str): Database name.

Routes:
    - '/' : Renders the index page.
    - '/users' (GET) : Retrieves and renders the list of users.
    - '/users' (POST) : Creates a new user based on the provided form data.
    - '/login' (POST) : Logs in a user based on the provided JSON data.
    - '/register' (POST) : Registers a new user based on the provided JSON data.

"""
import os
from flask import Flask, jsonify, request, render_template, redirect
from flask_login import LoginManager, login_user
from sqlalchemy import exc

from models import db, User

app = Flask(__name__, template_folder='../ui/templates',
            static_folder='../ui/static')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
    Load user data based on the provided user ID.

    Parameters:
    - user_id (int): The ID of the user to be loaded.

    Returns:
    - User or None: The User object if the user is found, None otherwise.
    """
    return User.query.get(int(user_id))


DB_HOST = os.environ.get('DB_HOST', 'postgresql_db')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://user:password@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db.init_app(app)

with app.app_context():
    # db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
    db.create_all()


@app.route('/')
def index():
    """
    Render the index page.

    Returns:
    - flask.Response: The rendered HTML response.
    """
    return render_template('index.html')


@app.route('/users', methods=['GET'])
def get_users():
    """
    Retrieve and render the list of users.

    Returns:
    - flask.Response: The rendered HTML response.
    """
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user based on the provided form data.

    Returns:
    - flask.Response: A redirect response.
    """
    data = request.form.to_dict()
    print(data)
    new_user = User(username=data['username'],
                    password=data['password'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return redirect('/login')


@app.route('/login', methods=['POST'])
def login():
    """
    Log in a user based on the provided JSON data.

    Returns:
    - flask.Response: JSON response containing user_id on success, or an error message on failure.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        login_user(user)
        return jsonify({'user_id': user.id}), 200
    return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user based on the provided JSON data.

    Returns:
    - flask.Response: JSON response indicating the registration status.
    """
    data = request.get_json()
    new_task = User(username=data.get('username'), email=data.get(
        'email'), password=data.get('password'))
    db.session.add(new_task)
    try:
        db.session.commit()
        return jsonify({'message': 'User registered successfully.'}), 200
    except exc.SQLAlchemyError:
        return jsonify({'message': 'User was not registered successfully.'}), 402


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
