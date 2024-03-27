from h2ogpte import H2OGPTE
# from flask import current_app as app, jsonify, request
import os
from dotenv import load_dotenv

load_dotenv(os.path.join("..", "..", ".env"))

client = H2OGPTE(
    address=os.getenv('H2O_ADDRESS'),
    api_key=os.getenv('H2O_COLLECTIOM_API_KEY'),
)

#use an exsited collection and create new chat session
chat_session_id = client.create_chat_session_on_default_collection()
default_collection = client.get_default_collection()
collection_id = default_collection.id
# collection_id = client.create_collection(
#     name='Resume',
#     description='ResumeAnalysis',
# )