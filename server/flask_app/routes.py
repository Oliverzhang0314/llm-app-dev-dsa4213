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

        # current the app is customized for software engineer role

        position = "software engineer"
        region = "singapore"
        department = "R&D"
        
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
    
@app.route('/rag/summary', methods=['GET','POST'])
def rag_summary():
    """
    Endpoint for summarizing the documents in the collection.

    Returns:
        Response: JSON response with summaries of the documents.
    """
    try:
        filenames=request.get_json().get('filenames')
        summaries = rag_summary_service(filenames)
        success_message = jsonify({"summaries":summaries})
        response = make_response(success_message,200)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/candidate/recommendation/table', methods=['GET'])
def candidate_rank():
    """
    Endpoint for getting the candidate recommendation table.

    Returns:    
        Response: JSON response with the candidate recommendation table.
    """
    try:
        position = request.args.get('position', "position_applied")
        region = request.args.get('region', "region")
        dept = request.args.get('dept', "department")
        limit = request.args.get('limit', 10)
        return jsonify(candidates_table(position, region, dept, limit))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/candidate/recommendation/radar-plot', methods=['GET'])
def candidate_radar_plot():
    """
    Endpoint for getting the candidate recommendation radar plot.

    Returns:
        Response: JSON response with the candidate recommendation radar plot.
    """
    try:
        position = request.args.get('position', "position_applied")
        region = request.args.get('region', "region")
        dept = request.args.get('dept', "department")
        limit = request.args.get('limit', 4)
        return jsonify(radar_plot(position, region, dept, limit))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/candidate/experience-levels', methods=['GET'])
def candidate_experience_distribution():
    """
    Endpoint for getting the candidate experience distribution.

    Returns:    
        Response: JSON response with the candidate experience distribution.
    """
    try:
        position = request.args.get('position', "position_applied")
        region = request.args.get('region', "region")
        dept = request.args.get('dept', "department")
        return jsonify(experience_distribution(position, region, dept))
    except Exception as e:
        return jsonify({'error': str(e)}), 500