import os
from flask import current_app as app, jsonify, request, make_response
from werkzeug.utils import secure_filename
from utils import *
from .services.rag_service import *
from .services.recommendation_service import *
from .services.profile_service import *


@app.route('/')
def index():
    return "welcome to flask server"
@app.route('/file/upload', methods=['GET','POST'])
def upload_file():
    if 'file' not in request.files:
        error_message = jsonify({'status':'No file uploaded.'})
        response = make_response(error_message, 400)
        return response

    files = request.files.getlist("file")
    filenames=[]

    for file in files:
        if file.filename == '':
            error_message = jsonify({'status','No file selected'})
            response = make_response(error_message, 400)
            return response
    
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filenames.append(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))               
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    try:
        # rag_file_upload_service(filenames)
        profile = create_profile()
        data={
            'status': 'File uploaded suceessfully',
            'data' : profile
        }
        response = make_response(data, 200)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#TODO: create rag_query api by using rag_query_service
@app.route('/rag/query', methods=['GET','POST'])
def rag_query():
    try:
        queries = request.get_json().get('queries')
        replies = rag_query_service(queries)
        success_message = jsonify({"replies":replies})
        response = make_response(success_message, 200)
        return response
    except Exception as e:
        return jsonify({'error':str(e)}), 500
        
@app.route('/rag/summary', methods=['GET','POST'])
def rag_summary():
    try:
        filenames=request.get_json().get('filenames')
        summaries = rag_summary_service(filenames)
        success_message = jsonify({"summaries":summaries})
        response = make_response(success_message,200)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#TODO: use pre-defined prompts to generate candidate profile and send to frontend to build dashboard 
@app.route('/candidate/profile',methods=['GET','POST'])
def candidate_profile():
    
    pass

#TODO: the recommendation feature 
@app.route('/candidate/recommendation', methods=['GET', 'POST'])
def candidate_rank():
    pass