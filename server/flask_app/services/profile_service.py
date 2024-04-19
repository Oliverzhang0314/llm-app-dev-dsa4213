from flask import current_app as app
from .rag_service import rag_query_service
import mysql.connector
import json
from dotenv import load_dotenv
import os
import re

# Load environment variables from the .env file
load_dotenv(os.path.join("..", "..", "..", ".env"))

def connect_to_db():
    connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        # port=app.config['MYSQL_PORT']
    )
    return connection

def create_profile(filenames:list, position:str, region:str, department:str):

    # Connect to the MySQL database
    connection = connect_to_db()

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

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
        candidate's api design experience score with a float ranging from 0-10 as apiDesignExperience (0 if Nan), \
        candidate's framework Knowledge score with a float ranging from 0-10 as framework knowledge (0 if Nan), \
        candidate's database skills score with a float ranging from 0-10 as databseSkill (0 if Nan), \
        candidate's cybersecurity knowledge score with a float ranging from 0-10 as cybersecurityKnowledge(0 if Nan), \
        candidate's app development experience score with a float ranging from 0-10 as appDevExperience(0 if Nan), \
        "
    ]
    # use predefined prompts to query LLM
    replies = rag_query_service(prompts, filenames)

    # Use regex to extract JSON information
    json_data = re.search(r'{.*}', replies[prompts[0]].replace("\n", ""))
    if json_data:
        json_data = json_data.group()
    else:
        raise ValueError("No JSON data extracted from the replied natural language sentence")

    # parse the replied natural language sentences to structured data
    profile = json.loads(json_data)
    print(profile)


    # store the extracted data in database
    sql = """INSERT INTO candidates 
            (candidate_name, 
            candidate_gender,
            candidate_experience, 
            candidate_MostRecenJobTitle, 
            candidate_education, 
            candidate_strength, 
            candidate_MostRescentJobTime, 
            apiDesignExperience, 
            frameworkKnowledge, 
            databaseSkill, 
            cybersecurityKnowledge,
            appDevExperience, 
            position_applied, 
            region, 
            department) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            
    cursor.execute(
        sql, 
        (profile.get('candidateName'), 
        profile.get('candidateGender'),
        profile.get('candidateExperience'), 
        profile.get('candidateMostRecentJobTitle'), 
        profile.get('candidateEducation'), 
        profile.get("candidateStrength"), 
        profile.get("candidateMostRecentJobTime"), 
        profile.get("apiDesignExperience"), 
        profile.get("frameworkKnowledge"), 
        profile.get("databaseSkill"), 
        profile.get("cybersecurityKnowledge"),
        profile.get("appDevExperience"), 
        position, 
        region, 
        department))

    connection.commit()
    cursor.close()
    connection.close()
    
    return profile

