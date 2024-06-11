from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.abspath("config.ini"))

app = Flask(__name__)

app.config["MONGO_URI"] = config["PROD"]["DB_URI"]

mongo = PyMongo(app).cx['quiz']



from Quiz import routes