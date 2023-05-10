import requests
import json

data = {'username': 'NC Kumar8', 'restauranttype': 'Pub, Fast Food, Date Night', 'cuisine':'Asian, European, Irish', 'rating':'2.5 to 3.5', 'price':'€€', 'subreddits': 'programming, productivity, scifi, movies, europe, television, cars, gamedev, trailers, announcements, hbo, coding, NetflixBestOf, teslamotors, ProgrammerHumor, AskEurope, AmazonPrimeVideo, DisneyPlus', 'interests':'business--events, food-and-drink--events, health--events, music--events'}
headers = {'Content-Type': 'application/json'}
response = requests.post('http://localhost:5000/user_registration', headers=headers, json=data)

print(response.text)
