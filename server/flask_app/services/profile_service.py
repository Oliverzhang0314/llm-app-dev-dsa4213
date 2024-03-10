from flask import current_app as app
from .rag_service import rag_query_service
import pymysql.cursors

# connection = pymysql.connect(
#     host=app.config['MYSQL_HOST'],
#     user=app.config['MYSQL_USER'],
#     password=app.config['MYSQL_PASSWORD'],
#     database=app.config['MYSQL_DB'],
#     cursorclass=pymysql.cursors.DictCursor
# )

#TODO: design prompt to generate useful results
prompts = [
    'prompt1', 
    'prompt2', 
    'prompt3'
    ]


def candidate_profile(filenames, prompts=prompts):
    """_summary_

    Args:
        filenames (list): candidate resumes
        prompts (list, optional): pre-defined prompts. Defaults to prompts.

    Returns:
        dict: a hash table with candidates and their corresponding profile data
    """
    
    # use predefined prompts to query LLM
    replies = rag_query_service(filenames, prompts)

    # TODO:parse the replied natural language sentences to structured data
    profile = {}

    # TODO:store the extracted data in database
    with connection:
        with connection.cursor() as cursor:
            sql = " "
            cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

    return profile
