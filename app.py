import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from dotenv import load_dotenv 
 

load_dotenv()
app = Flask(__name__)
#app.secret_key = os.getenv('SECRET_KEY')
db_user = os.getenv('DB_USER') 
db_password = os.getenv('DB_PASSWORD') 
db_host = os.getenv('DB_HOST') 
db_name = os.getenv('DB_NAME') 
db_port = os.getenv('DB_PORT')   
 
app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}") 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


def authenticate_client(username, password):
    user = User.query.filter_by(username=username).first()
    if user :
        return True
    else:
        return False


def store_client_in_database(username, password):
    username = request.form['username']     
    password = request.form['password']  
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if authenticate_client(request.form['username'], request.form['password']):  
            username_= request.form['username']       
            return render_template('client.html',username_=username_)
        else:
            flash('Please provide correct info')
            return redirect('/login?error=1')
    else:
        # Handle GET request, render login page
        return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signUp.html')


@app.route('/client_signup', methods=['POST'])
def client_signup():
    username = request.form['username']
    password = request.form['password']
    store_client_in_database(username, password)
    return redirect('/login')


@app.route('/provider')
def provider():
    return render_template('provider.html')


@app.route('/client')
def client():
    return render_template('client.html')


@app.route('/book', methods=['POST'])
def book():
    user_email = request.form.get('user_email')
    email_params = {
        "from": "contact@achrafsani.xyz",
        "to": user_email,
        "subject": "Your Booking Confirmation",
        "content": "Thank you for booking with us! Your appointment is confirmed."
    }
    invoke_email_function(email_params)  
    return redirect(url_for('client'))


def invoke_email_function(args):
    url = 'https://faas-lon1-917a94a7.doserverless.co/api/v1/web/fn-e539efa2-934c-43fd-832b-e55fc2b9dd63/sample/emails'
    data = {
        'from': args.get("from"),
        'to': args.get("to"),
        'subject': args.get("subject"),
        'content': args.get("content")
    }
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Email sent successfully")
        flash('Booking successful! Check your email for confirmation.')
    elif response.status_code == 400:
        flash('Failed to send email')
    else:       
        flash('Booking successful! Check your email for confirmation.')
        print("Status Code:", response.status_code)
        print("Response:", response.text)


@app.route('/get_information', methods=['GET'])
def get_information():
    arg=request.args.get('provider_id','not found')
    return render_template('provider.html',arg=arg)


@app.route('/get_client_information', methods=['GET'])
def get_client_information():
    client_username = request.args.get('username', 'not found')
    provider_id = request.args.get('calendar_id', 'not found')
    return render_template('client.html', provider_id=provider_id,client_username=client_username)


@app.route('/submit_datetime', methods=['GET'])
def submit_datetime():
    selected_date = request.form['selectedDate']
    selected_time = request.form['selectedTime']
    datetime_string = f"{selected_date}T{selected_time}:00"
    return redirect(f"https://google.achrafsani.xyz/create_event?title=TEST&start_date={datetime_string}&end_date={datetime_string}")
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
