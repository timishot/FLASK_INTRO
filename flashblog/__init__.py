import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

app.config['SECRET_KEY'] = 'bbd123498b9401f18479f4e5e705963d'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://timishot:Timilehin1@localhost:3306/flaskblog"
db = SQLAlchemy(app)
bcrypt =  Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = "info"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

from flashblog.users.route import users
from flashblog.posts.route import posts
from flashblog.main.route import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)