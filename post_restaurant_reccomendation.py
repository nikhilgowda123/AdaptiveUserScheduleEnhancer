import requests
import json

data = {'userid': '20'}
headers = {'Content-Type': 'application/json'}
response = requests.post('http://localhost:5000/generate_res_recommendation', headers=headers, json=data)

print(response.text)