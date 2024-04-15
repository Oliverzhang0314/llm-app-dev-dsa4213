import os 

baseurl = os.path.abspath(os.path.dirname(__file__))

class Config:
    H2O_API_KEY = 'sk-33L5yNLSb3gX4GwPjZf7sV5o9pI3YgeY1E0kj5yHI7ajqbAs'
    H2O_COLLECTIOM_API_KEY = 'sk-QxCDdaRYFHrw3fZLQ8b0EcQmikRNENWqsPkrXi2af928q1KB'
    H2O_ADDRESS = 'https://h2ogpte.genai.h2o.ai'
    UPLOAD_FOLDER = './docs'

    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'wang20020723'
    MYSQL_DB = 'dsa4213'