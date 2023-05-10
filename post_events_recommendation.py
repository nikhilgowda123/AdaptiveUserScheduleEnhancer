import requests
import json

data = {'userid': '3', 'time': "2023-04-10T10:40"}
headers = {'Content-Type': 'application/json'}
response = requests.post('http://localhost:5000/generate_event_recommendation', headers=headers, json=data)

print(response.json())