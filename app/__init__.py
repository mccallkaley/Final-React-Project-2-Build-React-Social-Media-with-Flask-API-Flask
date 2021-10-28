from flask import Flask
from config import Config 
from flask_login import LoginManager #to log users in and out and maintain the session
from flask_sqlalchemy import SQLAlchemy #this talk to the database
from flask_migrate import Migrate #this makes altering the db a lot easier




# app instaniation
app = Flask(__name__)
app.config.from_object(Config)

# init login manager
login = LoginManager(app)
# This is where you will be sent if you are not logged in
login.login_view = 'login'

# Stuff to work with the DB

# inits the database
db = SQLAlchemy(app)

migrate = Migrate(app, db)



from app import routes
