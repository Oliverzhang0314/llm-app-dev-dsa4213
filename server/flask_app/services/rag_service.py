##!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Date    : 09/03/2024
# @Author  : Jianig Wang
# @Email   : jianingwang124@gmail.com
# @File    : rag_service.py

from h2ogpte import H2OGPTE
from flask import current_app as app, jsonify, request
import os

client = H2OGPTE(
    address=app.config['H2O_ADDRESS'],
    api_key=app.config['H2O_COLLECTIOM_API_KEY'],
)

#use an exsited collection and create new chat session
chat_session_id = client.create_chat_session_on_default_collection()
default_collection = client.get_default_collection()
collection_id = default_collection.id
# collection_id = client.create_collection(
#     name='Resume',
#     description='ResumeAnalysis',
# )

def rag_file_upload_service(filenames:list, client=client, collection_id=collection_id):
    
    upload_files=[]
    
    for filename in filenames:  
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
            upload_files.append(client.upload(os.path.join(app.config['UPLOAD_FOLDER'], filename), f))
    print(upload_files)

    # Ingest documents (Creates previews, chunks and embeddings)
    client.ingest_uploads(collection_id, upload_files)


def rag_summary_service(client=client, collection_id=collection_id):
    """generate summary of each documents by h2ogpt 

    Args:
        filenames (list): uploaded files
        client (_type_, optional): h2ogpt client. Defaults to client.
        collection_id (_type_, optional): h2ogpt collection_id. Defaults to collection_id.

    Returns:
        list: summaries to documents
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

    
def rag_query_service(queries:list, client=client, collection_id=collection_id):
    """ This method is used to genenrate replies to queries by h20gpt 

    Args:
        filenames (list): uploaded files
        queries (list): an array of prompts
        client (_type_, optional): h2ogpt client. Defaults to client.
        collection_id (_type_, optional): h2ogpt collection_id. Defaults to collection_id.

    Returns:
        dict: an hashmap of replies corresponding to each queries
    """

    # Create a chat session
    chat_session_id = client.create_chat_session_on_default_collection()

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
                    if i == 3:
                        replies[q] = "Timed out after 3 attempts. Please try again later."
                        break
                    continue
    
    return replies