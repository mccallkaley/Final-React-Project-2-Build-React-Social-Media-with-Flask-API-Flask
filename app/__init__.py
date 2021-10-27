from flask import Flask
from config import Config 

# app instaniation
app = Flask(__name__)
app.config.from_object(Config)

from app import routes
