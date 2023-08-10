import os
from flask import Flask
from routes import pages
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
def create_app():
    app=Flask(__name__)
    app.register_blueprint(pages)
    client = MongoClient(os.environ.get("MONGODB_URI"))
    app.db = client.habittracker

    return app