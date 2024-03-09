import os 

baseurl = os.path.abspath(os.path.dirname(__file__))

class Config:
    H2O_API_KEY = 'sk-glsJVfy19D185FHPSzWyAB0vpFbVWbBF6gq9gsVUjPBi52oM'
    H2O_COLLECTIOM_API_KEY = 'sk-2x55Qp1XzYRTgslJYdgDMEYKyRVtSxZbFsVtB4lsfxrMgdNu'
    H2O_ADDRESS = 'https://h2ogpte.genai.h2o.ai'
    UPLOAD_FOLDER = './docs'

    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'your_username'
    MYSQL_PASSWORD = 'your_password'
    MYSQL_DB = 'your_database_name'