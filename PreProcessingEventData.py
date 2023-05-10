import pandas as pd
from nltk.corpus import stopwords
import numpy as np
from datetime import datetime
from geopy.geocoders import Nominatim


def get_start_date_end_date(date_range):
    data_value = []
    get_split_str = str(date_range).split("-")
    for str_splits in get_split_str:
        val = str_splits.split(",")
        for ele in val:
            temp = ele.split(" ")
            for t in temp:
                if t.__contains__(":"):
                    data_value.append(t.replace("IST", ""))
    if (len(data_value) == 0):
        return None
    else:
        return data_value


def get_lat_long(adr):
    geolocator = Nominatim(user_agent="my-app")
    location = geolocator.geocode(adr)
    if (location != None):
        return [(location.latitude, location.longitude)]
    return location


def convert_string_date(str_date):
    try:
        if (not str_date == None):
            date_obj = datetime.strptime(str_date, "%a, %b %d, %I:%M %p %Y")
            date_np = np.datetime64(date_obj)
            return date_np
        return None
    except:
        return None


def clear(data):
    data = data.lower()
    data = data.split()
    data_keywords = [word for word in data if word not in stopwords.words('english')]
    merged_data = " ".join(data_keywords)
    return merged_data


def clear_event_list(list_value):
    list_str = str(list_value).replace(",", "")
    data = list_str.lower()
    data = data.split()
    data_keywords = [word for word in data if word not in stopwords.words('english')]
    merged_data = " ".join(data_keywords)
    return merged_data


events_data = pd.read_csv("EventBrite_Data.csv")
events_data = events_data[~events_data['Event_Summary'].isnull()]
events_data['Time_Ranges'] = events_data['Event_Date_Range'].apply(get_start_date_end_date)
events_data = events_data[~events_data['Event_Description'].isnull()]
events_data = events_data[~events_data['Event_Time'].isnull()]
events_data['Event_Tag_List'] = events_data['Event_Tag_List'].apply(
    lambda x: str(x).replace("[", "").replace("]", "").replace("#", "").replace("'", "").replace("_", " "))
events_data['Event_Time_updates'] = events_data['Event_Time'].apply(lambda x: (x.split("+"))[0] + " 2023")
events_data['Event_Time_updates'] = events_data['Event_Time_updates'].apply(convert_string_date)
events_data['Event_Cat'] = events_data['Event_Cat'].apply(lambda x: x.replace("--events", "").replace("-", " "))
events_data['Event_Summary_cleared'] = events_data['Event_Summary'].apply(clear)
events_data['Event_Description_cleared'] = events_data['Event_Description'].apply(clear)
events_data['consolidated_Data'] = events_data['Event_Summary_cleared'] + str(" ") + events_data[
    'Event_Description_cleared'] + str(" ") + events_data['Event_Cat'] + str(" ") + events_data['Event_Tag_List']
events_data = events_data[
    ['Event_Cat', 'Event_brite_url', 'Event_Name', 'Event_Time', 'Event_Link', 'Event_Location', 'Event_Title',
     'Ticket_Fare', 'Event_Time_updates', 'consolidated_Data']].drop_duplicates()
events_data.reset_index(inplace=True)
events_data = events_data.rename(columns={'index': 'Event_Id'})
events_data.to_csv("Events_Data.csv", index=False)
