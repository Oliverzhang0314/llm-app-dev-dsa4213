import os
from flask import current_app as app, jsonify, request, make_response
from werkzeug.utils import secure_filename
from utils import *
from .services.rag_service import *
from .services.recommendation_service import *
from .services.profile_service import *

@app.route('/')
def index():
    """
    Endpoint for the root URL.
    """
    return "Welcome to the DSA4213 Group Whisper server"

@app.route('/file/upload', methods=['GET','POST'])
def upload_file():
    """
    Endpoint for uploading files and generating candidate profile.

    Returns:
        Response: JSON response indicating success or failure.
    """
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
        # parese reqeust to get arguments
        
        # position = request.form.get('position')
        # region = request.form.get('region')
        # department = request.form.get('department')
        
        position = "software engineer"
        region = "singapore"
        department = "swe"
        
        # generate candidate profile
        profile = create_profile(filenames, position, region, department)
        data={
            'status': 'File uploaded successfully',
            'data' : profile
        }
        response = make_response(data, 200)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rag/query', methods=['POST'])
def rag_query():
    """
    Endpoint for querying the RAG service.

    Returns:
        Response: JSON response with replies from the RAG service.
    """
    try:
        queries = request.get_json().get('queries')
        replies = rag_query_service(queries)
        success_message = jsonify({"replies":replies})
        response = make_response(success_message, 200)
        return response
    except Exception as e:
        return jsonify({'error':str(e)}), 500
        
