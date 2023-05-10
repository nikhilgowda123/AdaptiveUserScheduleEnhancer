import requests
import json


data = {'userid': 20, 'rating': -30, 'name':"Darkey Kellys", 'isevent':False}
headers = {'Content-Type': 'application/json'}
response = requests.post('http://localhost:5000/update_recommendation', headers=headers, json=data)

print(response.text)