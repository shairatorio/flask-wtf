# Importing Libraries
from flask import Flask, render_template
from flask_wtf import FlaskForm, CSRFProtect
from config import DevelopmentConfig, TestingConfig, ProductionConfig
from wtforms import (
    StringField, PasswordField, BooleanField,
    DecimalField, RadioField, SelectField, 
    TextAreaField, FileField, SubmitField
)
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os

# App Initialization
app = Flask(__name__)

# Load base config first
app.config.from_object('config.Config')

# Then override depending on environment
env = os.getenv('FLASK_ENV', 'development')
if env == 'development':
    app.config.from_object('config.DevelopmentConfig')
elif env == 'testing':
    app.config.from_object('config.TestingConfig')
else:
    app.config.from_object('config.ProductionConfig')

# Optional: Load additional config file if specified by environment variable
# Example usage:
# export FLASK_CONFIG_FILE=/path/to/config.py
if os.getenv('FLASK_CONFIG_FILE'):
    app.config.from_envvar('FLASK_CONFIG_FILE')

# Enable global CSRF protection
csrf = CSRFProtect(app) 

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ----------------- Forms -----------------
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    salary = DecimalField('Salary', validators=[InputRequired()])
    gender = RadioField('Gender', choices=[('M', 'Male'), ('F', 'Female')], validators=[InputRequired()])
    country = SelectField('Country', choices=[('US', 'United States'), ('CA', 'Canada')], validators=[InputRequired()])
    message = TextAreaField('Message', validators=[InputRequired()])
    profile_picture = FileField('Profile Picture')
    submit = SubmitField('Submit')
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Username Required'), Length(min=4, max=15, message='Username must be between 4 and 15 characters')])
    password = PasswordField('Password', validators=[InputRequired('Password Required'), Length(min=8, max=80)])
    submit = SubmitField('Submit')
    
# ----------------- Routes -----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    form = RegistrationForm()
    if form.validate_on_submit(): # CSRF checked automatically
        # Collect form data
        username = form.username.data
        password = form.password.data
        remember_me = form.remember_me.data
        salary = form.salary.data
        gender = form.gender.data
        country = form.country.data
        message = form.message.data
        profile_picture = form.profile_picture.data
        
        # Save the uploaded file 
        filename = None
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_picture.save(file_path)
        
        return f"""
        <h2>Form Submitted Successfully!</h2>
        Username: {username} <br> 
        Password: {generate_password_hash(password)} <br> 
        Remember Me: {remember_me} <br> 
        Salary: {salary} <br> 
        Gender: {gender} <br> 
        Country: {country} <br> 
        Message: {message} <br> 
        Profile Picture: <br>
        {'<img src="/' + file_path + '" width="150">' if filename else 'No file uploaded'}
        """
        
    return render_template('index.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = LoginForm()
    if form.validate_on_submit(): # CSRF checked automatically
        username = form.username.data
        return f"<h1>Signup Successful! Username: {username}</h1>"
    return render_template('signup.html', form=form)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])