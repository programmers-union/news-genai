# Example of how a api call is done in python

import requests

# URL of the API endpoint
url = 'https://example.com/api'

# Data to be sent in the POST request
data = {
    'key1': 'value1',
    'key2': 'value2'
}

# Optional headers
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-token-here'
}

# Making the POST request
response = requests.post(url, json=data, headers=headers)

# Handling the response
if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Failed with status code:", response.status_code)
    print("Response text:", response.text)
