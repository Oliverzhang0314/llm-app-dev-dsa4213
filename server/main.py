import os
from flask_app import create_app
app = create_app()
if __name__ =="__main__":
    app.run(
        host = '127.0.0.1',
        port = int(os.environ.get('port', 4000)),
        debug = True,
        use_reloader=True,
    )