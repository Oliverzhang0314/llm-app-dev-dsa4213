import os 

baseurl = os.path.abspath(os.path.dirname(__file__))

class Config:
    H2O_API_KEY = 'sk-33L5yNLSb3gX4GwPjZf7sV5o9pI3YgeY1E0kj5yHI7ajqbAs'
<<<<<<< HEAD
    H2O_COLLECTIOM_API_KEY = 'sk-uKjjDnUY9UQ7Dq2UCGQUZ61fkXzHf4wX2S9WLfqjkx0rQUmT'
=======
    H2O_COLLECTIOM_API_KEY = 'sk-QxCDdaRYFHrw3fZLQ8b0EcQmikRNENWqsPkrXi2af928q1KB'
>>>>>>> cc681ea782198ea724c98923e7d38eb7d9154f0e
    H2O_ADDRESS = 'https://h2ogpte.genai.h2o.ai'
    UPLOAD_FOLDER = './docs'

    MYSQL_HOST = 'localhost:3306'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'passwd'
    MYSQL_DB = 'dsa4213'