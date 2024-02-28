from flask import current_app as app


@app.route('/')
def home():
    return "<h1>this is the root url<h1>"

@app.route("/testingApi")
def test():
    return {"message":[1,2,3,4]}
