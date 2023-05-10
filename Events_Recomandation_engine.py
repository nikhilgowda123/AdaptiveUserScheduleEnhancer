import pandas as pd
import mysql.connector as connection
import pandas as pd
import numpy as np
import numpy as np
import re, math
from collections import Counter
import numpy as np
import pandas as pd
import operator
import json
from ast import literal_eval
from adaptiveRestaurants import get_rating_weight, calculate_final_score,push_data_to_database


class EventsRecomndationEngine():
    @staticmethod
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

    @staticmethod
    def event_clear(events):
        clean_list_events = ""
        eventslist = events.split(",")
        for event in eventslist:
            event = event.replace("--events", "")
            event = event.replace("-", " ")
            clean_list_events += str(event) + " "
        return clean_list_events

    @staticmethod
    def cosine_similarity_of(text1, text2):
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
            squared_sum_vector1 += vector1[i] ** 2
        for i in vector2.keys():
            squared_sum_vector2 += vector2[i] ** 2
        magnitude = math.sqrt(squared_sum_vector1) * math.sqrt(squared_sum_vector2)
        if not magnitude:
            return 0.0
        else:
            return float(dot_product) / magnitude

    @staticmethod
    def get_key_words_for_user_id(user_id):
        query = "Select * from userlist where userid = " + str(user_id) + " ;"
        res = EventsRecomndationEngine.get_data_from_database(query)
        if (not res.empty):
            res['interests'] = res['interests'].apply(EventsRecomndationEngine.event_clear)
            res['subreddits'] = res['subreddits'].apply(lambda x: x.replace(",", " "))
            res['keywords_events'] = res['interests'] + str("") + res['subreddits']
            return res.iloc[0]['keywords_events']
        else:
            return ""

    @staticmethod
    def get_event_recomandation_history(user_id):
        query = "select userid, recommendation_event from recommendation_history where userid = " + str(user_id) + " ;"
        res = EventsRecomndationEngine.get_data_from_database(query)
        if (not res.empty):
            impact_values = literal_eval(res.iloc[0]['recommendation_event'])
            return impact_values
        return dict()
    @staticmethod
    def userModelEventInit(userid):
        recom = EventsRecomndationEngine.eventRecommendationUserInit(userid)
        mysql_username = 'root'
        mysql_password = '!Gentoo123'
        mysql_host = '34.134.188.117'
        mysql_db = 'dev1_aa_gencal'
        mysql_table = f'event_user_model_{userid}'
        push_data_to_database(recom, mysql_username, mysql_password, mysql_host, mysql_db, mysql_table)
        return recom

    @staticmethod
    def eventRecommendationUserInit(user_id):
        user_key_words = EventsRecomndationEngine.get_key_words_for_user_id(user_id)
        events_data = pd.read_csv("Events_Data.csv")
        events_data.Event_Time_updates = events_data.Event_Time_updates.astype('datetime64[ns]')
        events_data['Event_similarity_score'] = events_data['consolidated_Data'].apply(
            lambda x: EventsRecomndationEngine.cosine_similarity_of(x, user_key_words))
        events_data['rating'] = 100
        events_data['scaledScore'] = None
        events_data['weight_rating'] = events_data['rating'].apply(get_rating_weight)
        events_data['scaledScore'] = events_data.apply(EventsRecomndationEngine.get_final_similarity_score, axis=1)
        events_data['userid'] = user_id
        return events_data


    @staticmethod
    def get_final_similarity_score(row):
        weight_rate = row['weight_rating']
        score = row['Event_similarity_score']
        simScoreScaled = calculate_final_score(score, weight_rate)
        return simScoreScaled

    @staticmethod
    def get_event_recomandation(user_id, free_time_start_str, free_time_end_str):
        query = f"select * from event_user_model_{user_id} ;"
        events_data = EventsRecomndationEngine.get_data_from_database(query)
        events_data.Event_Time_updates = events_data.Event_Time_updates.astype('datetime64[ns]')
        # free_time_start = np.datetime64('2023-04-05T03:30')
        # free_time_end = np.datetime64('2023-04-05T23:30')
        free_time_start = np.datetime64(free_time_start_str)
        free_time_end = np.datetime64(free_time_end_str)
        '''Getting the Events in the required Time range '''
        events_data_relavent = events_data[(events_data['Event_Time_updates'] >= free_time_start) & (
                events_data['Event_Time_updates'] < free_time_end)]
        if events_data_relavent.empty:
            return events_data_relavent
        events_data_relavent.sort_values('scaledScore', ascending=False, inplace=True)
        if len(events_data_relavent) < 5:
            events_data_relavent = events_data_relavent.rename(columns={'scaledScore': 'Final_score'})
            return events_data_relavent[
                ['Event_Id', 'Event_Name', 'Event_Cat', 'Event_Link', 'Event_Location', 'Ticket_Fare',
                 'Final_score']]

        res = events_data_relavent[
                  ['Event_Id', 'Event_Name', 'Event_Cat', 'Event_Link', 'Event_Location', 'Ticket_Fare',
                   'scaledScore']].iloc[0:5]
        res = res.rename(columns={'scaledScore': 'Final_score'})
        return res

    @staticmethod
    def updateEventUserModel(userid, rating, name):
        query = f"select * from event_user_model_{userid} ;"
        userModel = EventsRecomndationEngine.get_data_from_database(query)
        ogRating = list(userModel.loc[userModel['Event_Name'] == name, 'rating'])[0]
        score =  list(userModel.loc[userModel['Event_Name'] == name, 'Event_similarity_score'])[0]
        updated = ogRating + rating
        userModel.loc[userModel['Event_Name'] == name, 'rating'] = updated
        rating_Weight = get_rating_weight(updated)
        score_scaled = calculate_final_score(score, rating_Weight)
        userModel.loc[userModel['Event_Name'] == name, 'scaledScore'] = score_scaled
        mysql_username = 'root'
        mysql_password = '!Gentoo123'
        mysql_host = '34.134.188.117'
        mysql_db = 'dev1_aa_gencal'
        mysql_table = f'event_user_model_{userid}'
        push_data_to_database(userModel, mysql_username, mysql_password, mysql_host, mysql_db, mysql_table)
        return True
