import requests
import os

# URL of your Flask API endpoint
url = 'http://127.0.0.1:4000/file/upload'
file_name = 'dunder_mifflin.txt'
# Path to the file you want to upload
file_path = os.path.join(file_name)


# Open the file
with open(file_path, 'rb') as file:
    # Create a dictionary with the file data
    files = {'file': (file_path, file, 'text/plain')}  # 'file' is the form field name
     
    # Send a POST request with the file
    response = requests.post(url, files=files)

# Check the response
if response.status_code == 200:
    print(response.text)
else:
    print("Upload failed:", response.text)