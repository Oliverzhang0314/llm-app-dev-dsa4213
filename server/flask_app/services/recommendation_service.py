import mysql.connector
import pandas as pd
from flask import current_app as app, jsonify, request

def connect_to_db():
    """
    Connect to the MySQL database using the configuration provided in the Flask app.

    Returns:
        mysql.connector.connection.MySQLConnection: The connection object to the MySQL database.
    """
    connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        # port=app.config['MYSQL_PORT']
    )
    return connection

def candidates_table(position, region, dept, k: int=10):
    """
    Get the candidate data from the MySQL database.

    Parameters:
        position (str): The position applied for by the candidate.
        region (str): The region where the candidate is applying.
        dept (str): The department where the candidate is applying.
        k (int): The number of candidates to return.

    Returns:
        str: The candidate data in JSON format.
    """
    # Connect to the MySQL database
    connection = connect_to_db()

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Create optional filter
    position = (
        f"position_applied = '{position}'" 
        if position != "position_applied" 
        else f"position_applied = {position}"
    )
    
    region = (
        f"region = '{region}'" 
        if region != "region" 
        else f"region = {region}"
    )

    dept = (
        f"department = '{dept}'" 
        if dept != "department" 
        else f"department = {dept}"
    )


    # Execute a SELECT query
    query = f"""
            SELECT 
                candidate_name, 
                candidate_gender, 
                candidate_education, 
                candidate_experience, 
                candidate_strength, 
                candidate_MostRecenJobTitle,
                TIMESTAMPDIFF(
                    MONTH, 
                    STR_TO_DATE(CONCAT(candidate_MostRescentJobTime, '-01'), '%Y-%m-%d'), 
                    NOW()
                ) AS last_employed
            FROM candidates
            WHERE {position} AND {region} AND {dept}
            LIMIT {k}
            """
    cursor.execute(query)

    # Get column names
    field_names = [i[0] for i in cursor.description]
    
    # Fetch all the rows returned by the query
    rows = cursor.fetchall()    
    df = pd.DataFrame(rows, columns=field_names)

    # Close the cursor and the database connection
    cursor.close()
    connection.close()
    return df.to_json(orient="records", index=False)

def radar_plot(position, region, dept, k: int=4):
    """
    Get the candidate data from the MySQL database.

    Parameters:
        position (str): The position applied for by the candidate.
        region (str): The region where the candidate is applying.
        dept (str): The department where the candidate is applying.
        k (int): The number of candidates to return.

    Returns:
        str: The candidate data in JSON format.
    """
    # Connect to the MySQL database
    connection = connect_to_db()

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Create optional filter
    position = (
        f"position_applied = '{position}'" 
        if position != "position_applied" 
        else f"position_applied = {position}"
    )
    
    region = (
        f"region = '{region}'" 
        if region != "region" 
        else f"region = {region}"
    )

    dept = (
        f"department = '{dept}'" 
        if dept != "department" 
        else f"department = {dept}"
    )

    # Execute a SELECT query
    query = f"""
            SELECT 
                apiDesignExperience,
                frameworkKnowledge,
                databaseSkill,
                cybersecurityKnowledge,
                appDevExperience,
                (apiDesignExperience + frameworkKnowledge + databaseSkill + cybersecurityKnowledge + appDevExperience) AS total_score
            FROM candidates
            WHERE {position} AND {region} AND {dept}
            ORDER BY total_score DESC
            LIMIT {k}
            """
    
    cursor.execute(query)

    # Get column names
    field_names = [i[0] for i in cursor.description]
    
    # Fetch all the rows returned by the query
    rows = cursor.fetchall()    
    df = pd.DataFrame(rows, columns=field_names)
    df = df.drop(columns=["total_score"])

    # Close the cursor and the database connection
    cursor.close()
    connection.close()
    return df.to_json(orient="records", index=False)

def experience_distribution(position, region, dept):
    """
    Get the candidate data from the MySQL database.

    Parameters:
        position (str): The position applied for by the candidate.
        region (str): The region where the candidate is applying.
        dept (str): The department where the candidate is applying.

    Returns:
        str: The candidate data in JSON format.
    """

    # Connect to the MySQL database
    connection = connect_to_db()

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Create optional filter
    position = (
        f"position_applied = '{position}'" 
        if position != "position_applied" 
        else f"position_applied = {position}"
    )
    
    region = (
        f"region = '{region}'" 
        if region != "region" 
        else f"region = {region}"
    )

    dept = (
        f"department = '{dept}'" 
        if dept != "department" 
        else f"department = {dept}"
    )

    # Execute a SELECT query
    query = f"""
            SELECT 
                candidate_experience,
                COUNT(*) AS count
            FROM candidates
            WHERE {position} AND {region} AND {dept}
            GROUP BY candidate_experience
            """
    
    cursor.execute(query)

    # Get column names
    field_names = [i[0] for i in cursor.description]
    
    # Fetch all the rows returned by the query
    rows = cursor.fetchall()    
    df = pd.DataFrame(rows, columns=field_names)

    # Close the cursor and the database connection
    cursor.close()
    connection.close()
    return df.to_json(orient="records", index=False)
