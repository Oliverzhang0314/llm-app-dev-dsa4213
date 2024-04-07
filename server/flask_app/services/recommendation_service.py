import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(os.path.join("..", "..", "..", ".env"))

def candidates_table(k: int=10):
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        port=os.getenv("MYSQL_PORT")
    )

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # Execute a SELECT query
    query = f"""
            SELECT * 
            FROM candidates
            LIMIT {k}
            """
    cursor.execute(query)

    # Fetch all the rows returned by the query
    rows = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    connection.close()
    return rows