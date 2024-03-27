import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv(os.path.join("..", "..", ".env"))

# Database configuration
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': os.getenv('MYSQL_PORT')
}

# Route to handle the query
def recommendation(k=10):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Execute the query
        query = f"SELECT * FROM candidates LIMIT {k};"
        cursor.execute(query)

        # Fetch all the rows
        rows = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        print('Query executed successfully')
        return rows

    except mysql.connector.Error as error:
        return f'Error executing query: {error}'