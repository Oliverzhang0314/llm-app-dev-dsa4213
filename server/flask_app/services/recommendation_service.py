import os
import mysql.connector
from dotenv import load_dotenv
import pandas as pd

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

def candidates_table(k: int=10):
    # Connect to the MySQL database
    connection = connect_to_db()

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Execute a SELECT query
    query = f"""
            SELECT * 
            FROM candidates
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