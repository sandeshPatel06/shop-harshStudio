from flask import Flask, render_template, request, redirect, session, flash, jsonify
import os
from werkzeug.utils import secure_filename
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
import random

# Initialize the Flask application
app = Flask(__name__)

# Secret key for session management (should be kept secret in production)
app.secret_key = 'your_secret_key'  

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Directory to store uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image file extensions

# Database path (Stored locally on PC)
db_path = os.path.join(os.getcwd(), "product_management.db")

# Configure SQLite database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Initialize the SQLAlchemy database instance
db = SQLAlchemy(app)

# Twilio configuration
TWILIO_ACCOUNT_SID = 'ACb4e73d8e1e9c95dab4cb3d9ed5143697'
TWILIO_AUTH_TOKEN = '49743a20228c58eb88e1b45a2eff06a9'
TWILIO_PHONE_NUMBER = '+17603748781'
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Define the User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    phone_number = db.Column(db.String(15), unique=True, nullable=False)  # Unique phone number
    password_hash = db.Column(db.String(128), nullable=False)  # User password
    is_verified = db.Column(db.Boolean, default=False)  # Verification status

# Define the Product model for the database
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(100), nullable=False)  # Product name
    price = db.Column(db.Float, nullable=False)  # Product price
    description = db.Column(db.Text, nullable=False)  # Product description
    image_path = db.Column(db.String(255), nullable=True)  # Path to the product image

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# User registration form
class RegistrationForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

# OTP verification form
class OTPVerificationForm(FlaskForm):
    otp = StringField('Enter OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')

def send_otp(phone_number):
    otp = random.randint(100000, 999999)  # Generate a random 6-digit OTP
    message = client.messages.create(
        body=f'Your OTP is {otp}',
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    session['otp'] = str(otp)  # Store OTP in session
    return otp

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(phone_number=form.phone_number.data, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        send_otp(new_user.phone_number)  # Send OTP
        flash('Registration successful! Please verify your phone number.', 'success')
        return redirect(url_for('verify_otp', phone_number=new_user.phone_number))
    return render_template('register.html', form=form)

@app.route('/verify_otp/<phone_number>', methods=['GET', 'POST'])
def verify_otp(phone_number):
    form = OTPVerificationForm()
    if form.validate_on_submit():
        if form.otp.data == session.get('otp'):  # Compare with stored OTP
            user = User.query.filter_by(phone_number=phone_number).first()
            user.is_verified = True
            db.session
# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Start the server in debug mode