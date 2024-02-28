import os
from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        from . import routes


    @app.route('/#test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app