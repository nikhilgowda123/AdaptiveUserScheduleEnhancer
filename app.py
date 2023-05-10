import json
from flask import Flask, request
import pandas as pd
app = Flask(__name__)
import mysql.connector
from Events_Recomandation_engine import  EventsRecomndationEngine
import icalendar
from datetime import datetime, timedelta
import numpy as np
import IcsFreeTime
import adaptiveRestaurants
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def dbpush(data):
    cnx = mysql.connector.connect(user='root', password='!Gentoo123',
                                  host='34.134.188.117', port='3306',
                                  database='dev1_aa_gencal')
    cursor = cnx.cursor()

    for index, row in data.iterrows():
        insert_stmt = "INSERT INTO userlist (username, restauranttype, cuisine, rating, price, subreddits, interests) values(%s,%s,%s,%s,%s,%s,%s)"
        data = (row.username, row.restauranttype, row.cuisine, row.rating, row.price, row.subreddits, row.interests)
        cursor.execute(insert_stmt, data)

    cnx.commit()
    last_row_id = cursor.lastrowid
    cursor.close()
    return last_row_id


@app.route('/user_registration', methods=['POST'])
def handle_json():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.json
        username = data.get('username')
        restauranttype = data.get('restauranttype')
        cuisine = data.get('cuisine')
        rating = data.get('rating')
        price = data.get('price')
        subreddits = data.get('subreddits')
        interests = data.get('interests')
        dictionary = dict(username=username, cuisine=cuisine, rating=rating, price=price, subreddits=subreddits,
                          interests=interests, restauranttype=restauranttype)
        df = pd.DataFrame(dictionary, index=[0])
        last_row_id = dbpush(df)
        adaptiveRestaurants.userModelInit(last_row_id)
        EventsRecomndationEngine.userModelEventInit(last_row_id)
        return str(last_row_id)
    else:
        return "Content type is not supported."


@app.route('/generate_event_recommendation', methods=['POST'])
def generate_recommendation():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.json
        time = data.get('time')
        userid = data.get('userid')
        free_slots = IcsFreeTime.get_free_time_slots(time)
        combined_events = pd.DataFrame()
        for free_slot in free_slots:
            recommended_events = EventsRecomndationEngine.get_event_recomandation(userid,
                                                                                                              free_slot[
                                                                                                                  0],
                                                                                                              free_slot[
                                                                                                                  1])
            combined_events = pd.concat([combined_events, recommended_events])
        if len(combined_events) > 5:
            combined_events.sort_values('Final_score', ascending=False, inplace=True)
            combined_events = combined_events.iloc[:5]
        recommended_events_json = json.dumps(json.loads(combined_events.to_json(orient="records")))
        return recommended_events_json

    else:
        return "Content type is not supported."


@app.route('/generate_res_recommendation', methods=['POST'])
def generate_recommendation_res():
    now = datetime.now()
    today_12pm_ = now.replace(hour=12, minute=0, second=0, microsecond=0)
    today_3pm_ = now.replace(hour=15, minute=0, second=0, microsecond=0)
    today_6pm_ = now.replace(hour=18, minute=0, second=0, microsecond=0)
    today_9pm_ = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if (now > today_12pm_ and now < today_3pm_) or (now > today_6pm_ and now < today_9pm_):
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            data = request.json
            userid = data.get('userid')
            recommended_events = adaptiveRestaurants.getRestaurantRecommendation(int(userid))
            recommended_events_json = json.dumps(json.loads(recommended_events.to_json(orient="records")))
            return recommended_events_json

        else:
            return "Content type is not supported."
    else:
        return "{}"


@app.route('/update_recommendation', methods=['POST'])
def update_recommendation_res():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.json
        userid = data.get('userid')
        rating = data.get('rating')
        name = data.get('name')
        isevent = data.get('isevent')
        if not isevent:
            is_updated = adaptiveRestaurants.updateUserModel(userid, rating, name)
            return str(is_updated)
        else:
            isupdated = EventsRecomndationEngine.updateEventUserModel(userid,rating,name)
            return str(isupdated)
    else:
        return "Content type is not supported."
