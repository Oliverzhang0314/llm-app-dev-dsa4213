from h2ogpte import H2OGPTE
from flask import current_app as app, jsonify, request
import os
import json
# create a H2OGPT client
client = H2OGPTE(
    address=app.config['H2O_ADDRESS'],
    api_key=app.config['H2O_API_KEY'],
)

# create a collection
collection_id = client.create_collection(
    name='Resume',
    description='ResumeAnalysis',
)

def rag_file_upload_service(filenames:list, client=client, collection_id=collection_id):
    """
    Uploads files to the H2O platform and ingests them into the collection.

    Parameters:
        filenames (list): The list of filenames to upload and ingest.
        client (H2OGPTE): The H2OGPTE client to use for uploading and ingesting.
        collection_id (str): The ID of the collection to ingest the files into.

    Returns:
        None
    """
    upload_files=[]
    
    for filename in filenames:  
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
            upload_files.append(client.upload(os.path.join(app.config['UPLOAD_FOLDER'], filename), f))

    # Ingest documents (Creates previews, chunks and embeddings)
    client.ingest_uploads(collection_id, upload_files)

def rag_query_service(queries:list, filenames=None, client=client, collection_id=collection_id):
    """
    Query the RAG service with the provided prompts and return the replies.

    Parameters:
        queries (list): The list of prompts to query the RAG service with.
        filenames (list): The list of filenames to upload and ingest.
        client (H2OGPTE): The H2OGPTE client to use for querying.
        collection_id (str): The ID of the collection to query.

    Returns:
        dict: The replies from the RAG service for each prompt.
    """
    # upload the file to h2o platform
    if filenames:
        rag_file_upload_service(filenames)
    
    # Create a chat session
    chat_session_id = client.create_chat_session(collection_id)

    # Query the collection
    replies={}
    with client.connect(chat_session_id) as session:
        for q in queries:
            i = 0
            while True:
                try:
                    reply = session.query(
                        q,
                        timeout=100,
                    )
                    replies[q] = reply.content
                    break
                except TimeoutError:
                    i+=1
                    if i == 5:
                        replies[q] = "Timed out after 5 attempts. Please try again later."
                        break
                    continue
                except json.JSONDecodeError as json_error:
                    replies[q] = f"Error decoding JSON content: {json_error}"
                except Exception as e:
                # Handle other exceptions (e.g., connection errors)
                    replies[q] = f"Error occurred: {e}"
                    break
            break
    
    return replies


def rag_summary_service(client=client, collection_id=collection_id):
    """
    Summarize the documents in the collection.

    Parameters:
        client (H2OGPTE): The H2OGPTE client to use for summarization.
        collection_id (str): The ID of the collection to summarize.

    Returns:
        list: The summaries of the documents in the collection.
    """
    # Create a chat session
    chat_session_id = client.create_chat_session_on_default_collection()
    
    # Summarize each document
    summaries = []
    documents = client.list_documents_in_collection(collection_id, offset=0, limit=99)
    for doc in documents:
        summary = client.summarize_document(
            document_id=doc.id,
            timeout=60,
        )
        summaries.append(summary.content)
    
    return summaries