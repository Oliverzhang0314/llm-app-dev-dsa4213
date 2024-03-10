import os
from flask import Flask
from config import Config
from flask_cors import CORS
from flask_mysqldb import MySQL


def create_app(config_class=Config):
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    mysql = MySQL(app)
    # CORS(app)

    with app.app_context():
        from . import routes

    return app