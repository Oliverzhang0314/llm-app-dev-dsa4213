import os
from flask import Flask
from config import Config
from flask_cors import CORS
from flask_mysqldb import MySQL


def create_app(config_class=Config):
    
    mysql = MySQL(app)
    app = Flask(__name__)
    # CORS(app)
    app.config.from_object(config_class)

    with app.app_context():
        from . import routes
        from .services import rag_service

    return app