import os
from flask_app import create_app
from flask_cors import CORS

app = create_app()
cors = CORS(app)
if __name__ =="__main__":
    app.run(
        host = '0.0.0.0',
        port = int(os.environ.get('port', 4000)),
        debug = True,
        use_reloader=True,
    )