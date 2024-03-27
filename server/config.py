import os 

baseurl = os.path.abspath(os.path.dirname(__file__))

class Config:
    H2O_API_KEY = 'sk-k2onHXTiHNL72oXMDGBKus78srwSgYLemLp46Y6e1s1z7zvB'
    H2O_COLLECTIOM_API_KEY = 'sk-aWauf9sTFqCxw9DEDPHeWxcB4qfPBA3fhdL9WNVU2V8lidqc'
    H2O_ADDRESS = 'https://h2ogpte.genai.h2o.ai'
    UPLOAD_FOLDER = './docs'

    MYSQL_HOST = 'localhost:3306'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'passwd'
    MYSQL_DB = 'dsa4213'