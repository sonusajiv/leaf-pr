from flask import Flask, render_template, request, flash, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import re

app = Flask(__name__)
app.secret_key = "123"

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/userdetails'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Reflect the existing table structure
with app.app_context():
    db.Model.metadata.reflect(db.engine)

# Define the User model
class User(db.Model):
    __table__ = db.Model.metadata.tables['login']

# Define the route for registration


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))

        # Validate username, email, and password
        if not is_valid_username(username) or not is_valid_email(email) or not is_valid_password(password):
            flash('Please enter a valid username, email, and password!', 'error')
            return redirect(url_for('register'))

        # Create a new user object
        new_user = User(username=username, email=email, password=password)

        # Add the user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('home'))  # Redirect to home page after successful registration
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')

    return render_template('register.html')


def is_valid_username(username):
    # Username should contain at least one non-digit character, alphanumeric characters, and underscores
    return re.match("^(?=.*[a-zA-Z_])[a-zA-Z0-9_]+$", username) is not None

def is_valid_email(email):
    # Email validation using a simple regex pattern
    return re.match(r'^[\w\.-]+@[\w\.-]+$', email) is not None


def is_valid_password(password):
    # Password should be at least 8 characters long and contain at least one uppercase, one lowercase, one digit, and one special character
    return len(password) >= 8 and any(c.isupper() for c in password) and any(c.islower() for c in password) \
           and any(c.isdigit() for c in password) and any(c in "!@#$%^&*()-_=+{}[]|;:'\"<>,.?/" for c in password)


# Define the login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database to check if the entered credentials are valid
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            # If the user exists, store their email in the session to keep them logged in
            session['email'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to the home page after successful login
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('login'))  # Redirect back to the login page if login fails

    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/predict')
def prediction():
    return render_template('diseaseprediction.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)