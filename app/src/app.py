from flask import Flask, render_template
import requests
import socket
import os

from api.models import Task

app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')

# Get the internal IP of the Flask API service using its service name
API_SERVICE_NAME = 'flask-app-service'
API_PORT = 5000

# Check if running inside a Kubernetes cluster
if os.path.isfile("/var/run/secrets/kubernetes.io/serviceaccount/token"):
    API_IP = os.environ.get("KUBERNETES_SERVICE_HOST")
else:
    API_IP = os.environ.get('API_HOST')

API_URL = f'http://{API_IP}:{API_PORT}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_data')
def fetch_data():
    tasks = Task.query.all()
    data = [{'task': task.task} for task in tasks]
    return render_template('result.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)