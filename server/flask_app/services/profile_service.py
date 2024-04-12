from flask import current_app as app
from .rag_service import rag_query_service
import pymysql.cursors
import json
from dotenv import load_dotenv
import os
import re

# Load environment variables from the .env file
load_dotenv(os.path.join("..", "..", "..", ".env"))

connection = pymysql.connect(
     host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB"),
    port=int(os.getenv("MYSQL_PORT")),
    cursorclass=pymysql.cursors.DictCursor
)

#TODO: design prompt to generate useful results

def create_profile(position:str, region:str, department:str):
    """_summary_

    Args:
\        prompts (list, optional): pre-defined prompts. Defaults to prompts.

    Returns:
        dict: a hash table with candidates and their corresponding profile data
    """
    prompts = [
        f" \
        Please give me the following information in a json format: \
        candidate's name (NaN if not specified) as candidateName, \
        candidate's gender (NaN if not specified) as candidateGender, \
        candidate's experience score related to the position: {position}, with an int ranging from 1-10 as candidateExperience, \
        candidate's most recent job title as candidateMostRecentJobTitle, \
        candidate's highest education certificate as candidateEducation, \
        candidate's best technical strength in one word as candidateStrength, \
        candidate's most recent job ending time as candidateMostRecentJobTime, \
        candidate's workAttitude score with a float ranging from 1-10 as candidateWorkAttitude, \
        candidate's adaptability score with a float ranging from 1-10 as candidateAdaptability, \
        candidate's collaboration score with a float ranging from 1-10 as candidateCollaboration, \
        candidate's communication score with a float ranging from 1-10 as candidateCommunication, \
        candidate's workEthics score with a float ranging from 1-10 as candiateWorkEthics, \
        candidate's leaderShip score with a float ranging from 1-10 as candidateLeadership. \
        "
    ]
    # use predefined prompts to query LLM
    replies = rag_query_service(prompts)

    # Use regex to extract JSON information
    json_data = re.search(r'{.*}', replies[prompts[0]].replace("\n", ""))
    if json_data:
        json_data = json_data.group()
    else:
        raise ValueError("No JSON data extracted from the replied natural language sentence")

    # parse the replied natural language sentences to structured data
    profile = json.loads(json_data)

    # store the extracted data in database
    
    with connection:
        with connection.cursor() as cursor:
            sql = """INSERT INTO candidates 
            (candidate_name, 
            candidate_gender,
            candidate_experience, 
            candidate_MostRecenJobTitle, 
            candidate_education, 
            candidate_strength, 
            candidate_MostRescentJobTime, 
            candidate_workAttitude, 
            candidate_adaptability, 
            candidate_collaboration, 
            candidate_communication,
            candidate_workEthics, 
            candidate_leaderShip, 
            position_applied, 
            region, 
            department) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            
            cursor.execute(sql, 
            (profile.get('candidateName'), 
            profile.get('candidateGender'),
            profile.get('candidateExperience'), 
            profile.get('candidateMostRecentJobTitle'), 
            profile.get('candidateEducation'), 
            profile.get("candidateStrength"), 
            profile.get("candidateMostRecentJobTime"), 
            profile.get("candidateWorkAttitude"), 
            profile.get("candidateAdaptability"), 
            profile.get("candidateCollaboration"), 
            profile.get("candidateCommunication"),
            profile.get("candidateWorkEthics"), 
            profile.get("candidateLeadership"), 
            position, 
            region, 
            department))

            connection.commit()

    return profile

def retrive_profile():

    with connection:
        with connection.cursor() as cursor:
            sql = ""
