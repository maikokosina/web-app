from flask import Flask
from config import Config
from pymongo import MongoClient
from flask_avatars import Avatars

app = Flask(__name__)
app.config.from_object(Config)
avatars = Avatars(app)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.archive
users = db.users
pages = db.pages
access = db.access
files = db.files
	
from app import routes
