import os
import mysql.connector
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load environment variables from the .env file
load_dotenv(os.path.join("..", "..", "..", ".env"))

def connect_to_db():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        port=os.getenv("MYSQL_PORT")
    )
    return connection

def candidates_table(position, region, dept, k: int=10):
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
            SELECT name, gender, education, experience_level, strength, last_job,
            TIMESTAMPDIFF(MONTH, STR_TO_DATE(CONCAT(last_job_date, '-01'), '%Y-%m-%d'), NOW()) AS last_employed
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