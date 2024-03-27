
def upload_documents(client, collection_id,file_path):
    # Upload documents
    with open(file_path, 'rb') as f:
        dunder_mifflin = client.upload(file_path, f)       
    # Ingest documents (Creates previews, chunks and embeddings)
    client.ingest_uploads(collection_id, [dunder_mifflin])

def summarize_documents(client, collection_id):
    documents = client.list_documents_in_collection(collection_id, offset=0, limit=99)
    for doc in documents:
        summary = client.summarize_document(
            document_id=doc.id,
            timeout=60,
        )
        print(summary.content)
def create_and_query_chat_session(client, collection_id=None):
    if collection_id:
        # Create a chat session with a specific collection
        chat_session_id = client.create_chat_session(collection_id)
    else:
        # Create a chat session without a specific collection
        chat_session_id = client.create_chat_session()

    # Query the chat session
    with client.connect(chat_session_id) as session:
        reply = session.query(
            'How many paper clips were shipped to Scranton?',
            timeout=60,
        )
        print(reply.content)

        reply = session.query(
            'Did David Brent co-sign the contract with Initech?',
            timeout=60,
        )
        print(reply.content)

        reply = session.query(
            'Why is drinking water good for you?',
            timeout=60,
        )
        print(reply.content)

