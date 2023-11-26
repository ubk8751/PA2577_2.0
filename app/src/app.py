from flask import Flask, render_template
import requests
import socket
import os

app = Flask(__name__, template_folder='ui/templates')

# Get the internal IP of the Flask API service using its service name
API_SERVICE_NAME = 'flask-app-service'
API_PORT = 5000

# Check if running inside a Kubernetes cluster
if os.path.isfile("/var/run/secrets/kubernetes.io/serviceaccount/token"):
    API_IP = os.environ.get("KUBERNETES_SERVICE_HOST")
else:
    API_IP = os.environ.get('DB_HOST') # <------------------------------------------------

API_URL = f'http://{API_IP}:{API_PORT}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_data')
def fetch_data():
    response = requests.get(API_URL)
    data = response.json() if response.status_code == 200 else {'error': 'Failed to fetch data'}
    return render_template('result.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)