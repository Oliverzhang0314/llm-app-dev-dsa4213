import os 

baseurl = os.path.abspath(os.path.dirname(__file__))

class Config:
    H2O_API_KEY = 'sk-INgifCNRTjym4LkiLpzmZfds7qXjH0vOivg7288dOUTYtu6y'
    H2O_COLLECTIOM_API_KEY = 'sk-ohZPI6qLUowihiQG3ulMYcxwLLiEoROCEhqk0elgjbE50m3K'
    H2O_ADDRESS = 'https://h2ogpte.genai.h2o.ai'
    UPLOAD_FOLDER = './docs'

    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'wang20020723'
    MYSQL_DB = 'dsa4213'