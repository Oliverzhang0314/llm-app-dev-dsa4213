import os 

baseurl = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Configuration class for the Flask app.
    """
    H2O_API_KEY = 'sk-INgifCNRTjym4LkiLpzmZfds7qXjH0vOivg7288dOUTYtu6y'
    H2O_COLLECTIOM_API_KEY = 'sk-ohZPI6qLUowihiQG3ulMYcxwLLiEoROCEhqk0elgjbE50m3K'
    H2O_ADDRESS = 'https://h2ogpte.genai.h2o.ai'
    UPLOAD_FOLDER = './docs'

    # database container
    MYSQL_ROOT_PASSWORD='root'
    MYSQL_DATABASE='dsa4213'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'dsa4213'
    MYSQL_PORT = 3306

    # local database
    # MYSQL_HOST = 'localhost'
    # MYSQL_USER = 'root'
    # MYSQL_PASSWORD = 'root'
    # MYSQL_DB = 'dsa4213'
