import os
from flask import current_app as app, jsonify, request, make_response
from werkzeug.utils import secure_filename
from utils import *
from .services.rag_service import *


@app.route("/testingApi", methods=['GET'])
def test():
    data = {'sentence':"this is a testing message"}
    return jsonify(data),200

@app.route('/file/upload', methods=['GET','POST'])
def upload_file():
    if 'file' not in request.files:
        error_message = jsonify({'message':'No file uploaded.'})
        response = make_response(error_message, 400)
        return response

    file = request.files['file']

    if file.filename == '':
        error_message = jsonify({'message','No file selected'})
        response = make_response(error_message, 400)
        return response
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #TODO: upload file to servie file storage system
            success_message = jsonify({'message':'File uploaded successfully'})
            response = make_response(success_message, 200)
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/rag/query', methods=['GET'])
def rag_query():
    #TODO: create rag_query api by using rag_query_service
        pass

@app.route('/rag/summary', methods=['POST'])
def rag_summary():
    try:
        filenames=request.get_json().get('filenames')
        summaries = rag_summary_service(filenames)
        success_message = jsonify({"summaries":summaries})
        response = make_response(success_message,200)
        return response
        #TODO: create rag_summary api by using rag_summary_service
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#TODO: the recommendation feature