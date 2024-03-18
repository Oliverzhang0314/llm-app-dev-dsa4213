import os
from flask import Flask
from config import Config
#from flask_cors import CORS


def create_app(config_class=Config):
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    # CORS(app)

    with app.app_context():
        from . import routes

    return app