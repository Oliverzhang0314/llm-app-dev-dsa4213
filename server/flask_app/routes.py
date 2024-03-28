import os
from flask import current_app as app, jsonify, request, make_response
from werkzeug.utils import secure_filename
from utils import *
from .services.rag_service import *
from .services.profile_service import *
from .services.recommendation_service import *
import h2oeGPT 
from h2ogpte import H2OGPTE

client = H2OGPTE(
    address='https://h2ogpte.genai.h2o.ai',
    api_key='sk-uKjjDnUY9UQ7Dq2UCGQUZ61fkXzHf4wX2S9WLfqjkx0rQUmT',
)
chat_session_id= client.create_chat_session_on_default_collection()
collection_id=client.get_collection_for_chat_session(chat_session_id).id
if collection_id is not None:
    # Print or use the collection ID
    print("Collection ID:")
    print(collection_id)
else:
    print("Collection not found or error occurred.")

@app.route("/", methods=['GET'])
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
            response_from_upload = h2oeGPT.upload_documents(client,collection_id, filename)
            success_message = jsonify({
                'message': 'File uploaded and processed successfully',
                'collection_id': collection_id
            })
            response = make_response(success_message, 200)
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:
        error_message = jsonify({'message': 'Invalid file type. Allowed extensions: txt, pdf, png, jpg, jpeg, gif'})
        response = make_response(error_message, 400)
        return response

#TODO: create rag_query api by using rag_query_service
@app.route('/rag/query', methods=['GET','POST'])
def rag_query():
        pass

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