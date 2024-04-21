import os
from flask import Flask
from config import Config
#from flask_cors import CORS


def create_app(config_class=Config):
    """
    Create a Flask app using the provided configuration class.
    
    Parameters:
        config_class (Config): The configuration class to use for the app.

    Returns:
        Flask: The Flask app created using the provided configuration class.
    """
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    # CORS(app)

    with app.app_context():
        from . import routes

    return app