from flask import Flask, render_template
import requests

app = Flask(__name__)

# Replace this URL with your Flask API endpoint
API_URL = 'http://<EXTERNAL-IP>:5000'  # Replace <EXTERNAL-IP> with the actual external IP

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