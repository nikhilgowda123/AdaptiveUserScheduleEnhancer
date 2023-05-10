#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 19:59:50 2023

@author: abhik_bhattacharjee
"""

from yelpapi import YelpAPI
import pandas as pd
import requests
import regex
import emoji
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re, math
from collections import Counter
import operator
import mysql.connector as connection
from sqlalchemy import create_engine
import mysql.connector
nltk.download('vader_lexicon')
nltk.download('stopwords')

API_KEY = "n7nRxqkWHMKIbH0sy8WbG_cOvKD0wjmohJLwi-fruYdsZtYYhrrFAXfXz9DX-azKup5gs_QlOzXhu9WigvRw_HnTa5FeXgV1bsBmMoK4LZbYs3F9J3zWpCsNgroUZHYx"

def get_dublin_restaurants():
    headers = {
        'Authorization': 'Bearer ' + API_KEY,
    }
    params = {
        'location': 'Dublin',
        'categories': 'restaurants',
        'limit': 50,
    }
    response = requests.get('https://api.yelp.com/v3/businesses/search', headers=headers, params=params)
    results = response.json()['businesses']
    return results

def get_restaurant_details(business_id):
    headers = {
        'Authorization': 'Bearer ' + API_KEY,
    }
    response = requests.get(f'https://api.yelp.com/v3/businesses/{business_id}', headers=headers)
    result = response.json()
    return result

def get_restaurant_reviews(business_id):
    headers = {
        'Authorization': 'Bearer ' + API_KEY,
    }
    params = {
        'business_id': business_id,
        'limit': 50,
    }
    response = requests.get(f'https://api.yelp.com/v3/businesses/{business_id}/reviews', headers=headers, params=params)
    results = response.json()['reviews']
    return results

def get_all_reviews():
    restaurants = get_dublin_restaurants()
    all_reviews = []
    for restaurant in restaurants:
        business_id = restaurant['id']
        restaurant_details = get_restaurant_details(business_id)
        restaurant_reviews = get_restaurant_reviews(business_id)
        for review in restaurant_reviews:
            review['restaurant_name'] = restaurant_details['name']
            all_reviews.append(review)
    return all_reviews

def split_count(info):

    emoji_list = []
    data = regex.findall(r'\X', info)
    for word in data:
        if any(char in emoji.EMOJI_DATA for char in word):
            emoji_list.append(word)

    return len(emoji_list)

def get_titles(list_tags):
    list_key=""
    for ele in list_tags:
        list_key+=str(ele['title'])+" "
    return list_key

def cosineSimilarity(text1, text2):
        first = re.compile(r"[\w']+").findall(text1)
        second = re.compile(r"[\w']+").findall(text2)
        vector1 = Counter(first)
        vector2 = Counter(second)
        common = set(vector1.keys()).intersection(set(vector2.keys()))
        dot_product = 0.0
        for i in common:
          
            dot_product += vector1[i] * vector2[i]
        squared_sum_vector1 = 0.0
        squared_sum_vector2 = 0.0
        for i in vector1.keys():
            squared_sum_vector1 += vector1[i]**2
        for i in vector2.keys():
            squared_sum_vector2 += vector2[i]**2
        magnitude = math.sqrt(squared_sum_vector1) * math.sqrt(squared_sum_vector2)
        if not magnitude:
           return 0.0
        else:
           return float(dot_product) / magnitude

def userDetails(user_id):
        query = "select * from userlist where userid = " + str(user_id) + " ;"
        userDetails = get_data_from_database(query)
        userDetails["Key"] = userDetails["restauranttype"].astype(str) +"-"+ userDetails["cuisine"].astype(str) +"-"+ userDetails["rating"].astype(str) +"-"+ userDetails["price"].astype(str) +"-"+ userDetails["subreddits"].astype(str) +"-"+ userDetails["interests"].astype(str)
        return userDetails

def get_data_from_database(query):
        try:
            mydb = connection.connect(user='root', password='!Gentoo123',
                                      host='34.134.188.117', port='3306',
                                      database='dev1_aa_gencal', use_pure=True)
            result_dataFrame = pd.read_sql(query, mydb)
            mydb.close()  # close the connection
            return result_dataFrame
        except Exception as e:
            mydb.close()
            print(str(e))
            return pd.DataFrame()

def push_data_to_database(df, mysql_username, mysql_password, mysql_host, mysql_db, mysql_table):
    try:
        engine = create_engine(f'mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_db}')
        df.to_sql(name=mysql_table, con=engine, if_exists='replace', index=False)
        engine.dispose()
    except Exception as e:
        print("Error occurred while pushing data to MySQL table:", str(e))


def get_rating_weight(rating, q=100):

    m = (2*q) / 100
    b = -q
    return (m*rating) + b

def calculate_final_score(cs, r):
    amount = (cs / 100) * r
    return cs + amount

def dfOps():
    reviews = get_all_reviews()
    reviews_df = pd.DataFrame(reviews, columns=['id', 'rating', 'text', 'time_created', 'user', 'restaurant_name'])
    restaurants = get_dublin_restaurants()
    restaurants_df = pd.DataFrame(restaurants)
    reviews_df['emoji_count'] = reviews_df.text.apply(split_count)
    reviews_df['text'] = reviews_df['text'].str.replace('\n', ' ')
    stop = stopwords.words('english')
    reviews_df['text_stop_word_rem'] = reviews_df['text'].apply(lambda x: ' '.join([word.lower() for word in x.split() 
                                                               if word not in (stop)]))   
    sent_int = SentimentIntensityAnalyzer()
    for i in range(len(reviews_df['text_stop_word_rem'])):
        s = reviews_df['text_stop_word_rem'][i]
        sentiment = sent_int.polarity_scores(s)
        reviews_df.loc[i, "sent_scr"] = sentiment["compound"]
    
    reviews_grouped = reviews_df.groupby('restaurant_name')['text_stop_word_rem'].agg(lambda x: ' '.join(x)).reset_index()
    restaurants_df['categories_key_word']=restaurants_df['categories'].apply(get_titles)
    restaurants_df = restaurants_df.rename(columns={'name': 'restaurant_name'})
    reviews_grouped_new = pd.merge(restaurants_df, reviews_grouped, on='restaurant_name')
    reviews_grouped_new['Key'] = reviews_grouped_new['categories_key_word'].astype(str) +"-"+ reviews_grouped_new["text_stop_word_rem"].astype(str) +"-"+ reviews_grouped_new["price"].astype(str) +"-"+ reviews_grouped_new["rating"].astype(str)
    return reviews_grouped_new

def restaurantRecommendationInit(userDetails, reviews_grouped_new):
    score_dict = {}
    for index, row in reviews_grouped_new.iterrows():
        score_dict[index] = cosineSimilarity(row['Key'], userDetails["Key"][0])
    sorted_scores = sorted(score_dict.items(), key=operator.itemgetter(1), reverse=True)
    counter = 0
    resultDF1 = pd.DataFrame(columns=('userid', 'restaurant_name', 'Category', 'TestData', 'score', 'rating', 'scaledScore'))
    for i in sorted_scores:
       resultDF1 = resultDF1.append({'userid': userDetails["userid"][0], 'restaurant_name': reviews_grouped_new.iloc[i[0]]['restaurant_name'], 'Category': reviews_grouped_new.iloc[i[0]]['categories_key_word'], 'TestData': reviews_grouped_new.iloc[i[0]]['Key'], 'score': i[1]}, ignore_index=True)
       counter += 1
    resultDF1['rating'] = 100
    resultDF1['scaledScore'] = None
    for index, row in resultDF1.iterrows():
        rate = row['rating']
        ratingWeight = get_rating_weight(rate)
        simScoreScaled = calculate_final_score(row['score'], ratingWeight)
        resultDF1['scaledScore'][index] = simScoreScaled
    return resultDF1


def userModelInit(userid):
    user = userDetails(userid)
    reviews = dfOps()
    recom = restaurantRecommendationInit(user, reviews)
    mysql_username = 'root'
    mysql_password = '!Gentoo123'
    mysql_host = '34.134.188.117'
    mysql_db = 'dev1_aa_gencal'
    mysql_table = f'restaurant_user_model_{userid}'
    
    push_data_to_database(recom, mysql_username, mysql_password, mysql_host, mysql_db, mysql_table)
    return recom


def updateUserModel(userid, rating, name):
    query = f"select * from restaurant_user_model_{userid} ;"
    userModel = get_data_from_database(query)
    ogRating = userModel.loc[userModel['restaurant_name'] == name, 'rating']
    updated = ogRating + (rating)
    userModel.loc[userModel['restaurant_name'] == name, 'rating'] = updated
    # print(userModel.loc[userModel['restaurant_name'] == name, 'rating'])
    
    for index, row in userModel.iterrows():
        rate = row['rating']
        ratingWeight = get_rating_weight(rate)
        simScoreScaled = calculate_final_score(row['score'], ratingWeight)
        userModel['scaledScore'][index] = simScoreScaled
            
    mysql_username = 'root'
    mysql_password = '!Gentoo123'
    mysql_host = '34.134.188.117'
    mysql_db = 'dev1_aa_gencal'
    mysql_table = f'restaurant_user_model_{userid}'
    push_data_to_database(userModel, mysql_username, mysql_password, mysql_host, mysql_db, mysql_table)
    return True
    
def getRestaurantRecommendation(userid):
    restaurants = get_dublin_restaurants()
    restaurants_df = pd.DataFrame(restaurants)
    restaurants_df = restaurants_df.rename(columns={'name': 'restaurant_name'})
    query = f"select * from restaurant_user_model_{userid} ;"
    recommendations = get_data_from_database(query)
    recommendations = pd.merge(restaurants_df, recommendations, on='restaurant_name')
    recommendations.sort_values('scaledScore', ascending=False, inplace=True)
    recommendations = recommendations.iloc[0:5]
    return recommendations[['restaurant_name', 'url', 'review_count', 'rating_x', 'price', 'location', 'coordinates', 'phone']]