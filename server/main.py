import os
from flask_app import create_app

def run_flask_app():
    """
    Run the Flask application.

    This function creates a Flask app using create_app() from flask_app module,
    and then runs the app on the specified host and port.

    If executed directly (not imported), it runs the app in debug mode with auto-reloading.

    """
    app = create_app()
    if __name__ == "__main__":
        app.run(
            host='127.0.0.1',
            port=int(os.environ.get('PORT', 4000)),  # Environment variable for port
            debug=True,
            use_reloader=True,
        )