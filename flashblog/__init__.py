from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'bbd123498b9401f18479f4e5e705963d'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://timishot:Timilehin1@localhost:3306/flaskblog"
db = SQLAlchemy(app)
bcrypt =  Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "info"

from flashblog import routes