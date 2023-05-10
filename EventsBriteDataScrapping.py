import requests
from bs4 import BeautifulSoup
import pandas as pd


def getEventDetails(row):
    try:
        page = requests.get(row['Event_Link'])
        soup = BeautifulSoup(page.content, 'html.parser')
        fare_val = soup.find('div', class_='conversion-bar__body')
        fare = fare_val.text if fare_val else ''
        print(fare)
        event_value = soup.find('div', class_='event-details__main-inner')
        if event_value:
            start_date_ele = event_value.find('time')
            start_date = start_date_ele['datetime'] if start_date_ele else ''
            name = event_value.find('meta')['content']
            summary = event_value.find('p', class_='summary').text
        else:
            start_date=''
            name=''
            summary=''
        event_main = soup.find('div', class_='event-details__main')
        if not event_main:
            return start_date, name, summary, '', '', '', [], fare
        event_deatils_section = event_main.find('section', class_='event-details__section')
        if not event_deatils_section:
            return start_date, name, summary, '', '', '', [], fare
        event_details = event_deatils_section.find_all('div', class_='detail__content')
        if len(event_details)>1:
            date_range_val = event_details[0].find('span')
            date_range = date_range_val.text if date_range_val else ''
            location_val = event_details[1].find('p')
            location = location_val.text if location_val else ''
        else:
            date_range=''
            location=''
        descrption_val = event_main.find('div', class_='has-user-generated-content')
        descrption = descrption_val.text if descrption_val else ''
        tags_list_ele = event_main.find('div', class_='eds-l-mar-bot-12')
        if tags_list_ele:
            tags_list = tags_list_ele.find_all('li')
        else:
            tags_list = []
        tag_list = []
        for tag in tags_list:
            tag_list.append(tag.text)
        return start_date, name, summary, date_range, location, descrption, tag_list, fare
    except:
        return '', '', '', '', '', '', '', ''


events = ['business--events', 'food-and-drink--events', 'health--events', 'music--events', 'community--events',
          'auto-boat-and-air--events', 'charity-and-causes--events', 'family-and-education--events', 'fashion',
          'film-and-media--events', 'hobbies--events', 'home-and-lifestyle--events',
          'performing-and-visual-arts--events', 'government--events', 'spirituality--events',
          'school-activities--events', 'science-and-tech--events', 'holiday--events', 'sports-and-fitness--events',
          'travel-and-outdoor--events', 'other--events']

consolidate_dataframe = pd.DataFrame()
for event in events:
    Events_agg = []
    for i in range(1, 10):
        url = "https://www.eventbrite.com/d/ireland--dublin/%s/?page=%s" % (event, i)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        search_pannel = soup.find('section', class_='search-base-screen__search-panel')
        search_cards = search_pannel.find('div', class_='search-results-panel-content')
        events_data = search_cards.find('ul', class_='search-main-content__events-list')
        if not events_data:
            continue
        elements_pre_link = events_data.find_all('a', href=True)
        events_realted_data = events_data.find_all('div', class_='eds-event-card-content__primary-content')
        locations = events_data.find_all('div', class_='card-text--truncated__one')
        for index in range(len(events_realted_data)):
            value_dict = dict()
            link = events_realted_data[index].find('a', href=True, class_='eds-event-card-content__action-link')['href']
            time = events_realted_data[index].find('div',
                                                   class_='eds-event-card-content__sub-title eds-text-color--primary-brand eds-l-pad-bot-1 eds-l-pad-top-2 eds-text-weight--heavy eds-text-bm').text
            names_new = events_realted_data[index].find('div',
                                                        class_='eds-event-card__formatted-name--is-clamped eds-event-card__formatted-name--is-clamped-three eds-text-weight--heavy').text
            location_name = locations[index].text
            value_dict['Event_Cat'] = event
            value_dict['Page'] = i
            value_dict['Event_brite_url'] = url
            value_dict['Event_Name'] = names_new
            value_dict['Event_Time'] = time
            value_dict['Event_Link'] = link
            value_dict['Event_Location'] = location_name
            Events_agg.append(value_dict)
    df = pd.DataFrame(Events_agg)
    df.drop_duplicates(inplace=True)
    df[['Start_date_Event_Page', 'Event_Title', 'Event_Summary', 'Event_Date_Range', 'Event_Address',
            'Event_Description', 'Event_Tag_List', 'Ticket_Fare']] = df.apply(getEventDetails, axis=1,
                                                                              result_type='expand')
    consolidate_dataframe = pd.concat([consolidate_dataframe, df])
for event in events:
    Events_agg = []
    for i in range(1, 10):
        url = "https://www.eventbrite.com/d/ireland--dublin/%s--next-month/?page=%s" % (event, i)
        print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        search_pannel = soup.find('section', class_='search-base-screen__search-panel')
        search_cards = search_pannel.find('div', class_='search-results-panel-content')
        events_data = search_cards.find('ul', class_='search-main-content__events-list')
        if not events_data:
            continue
        elements_pre_link = events_data.find_all('a', href=True)
        events_realted_data = events_data.find_all('div', class_='eds-event-card-content__primary-content')
        locations = events_data.find_all('div', class_='card-text--truncated__one')
        for index in range(len(events_realted_data)):
            value_dict = dict()
            link = events_realted_data[index].find('a', href=True, class_='eds-event-card-content__action-link')['href']
            time = events_realted_data[index].find('div',
                                                   class_='eds-event-card-content__sub-title eds-text-color--primary-brand eds-l-pad-bot-1 eds-l-pad-top-2 eds-text-weight--heavy eds-text-bm').text
            names_new = events_realted_data[index].find('div',
                                                        class_='eds-event-card__formatted-name--is-clamped eds-event-card__formatted-name--is-clamped-three eds-text-weight--heavy').text
            location_name = locations[index].text
            value_dict['Event_Cat'] = event
            value_dict['Page'] = i
            value_dict['Event_brite_url'] = url
            value_dict['Event_Name'] = names_new
            value_dict['Event_Time'] = time
            value_dict['Event_Link'] = link
            value_dict['Event_Location'] = location_name
            Events_agg.append(value_dict)
    df = pd.DataFrame(Events_agg)
    df.drop_duplicates(inplace=True)
    df[['Start_date_Event_Page', 'Event_Title', 'Event_Summary', 'Event_Date_Range', 'Event_Address',
            'Event_Description', 'Event_Tag_List', 'Ticket_Fare']] = df.apply(getEventDetails, axis=1,
                                                                              result_type='expand')
    consolidate_dataframe = pd.concat([consolidate_dataframe, df])

print(consolidate_dataframe['Event_Cat'].unique())
print(consolidate_dataframe.head())
# consolidate_dataframe.drop_duplicates(inplace=True)
consolidate_dataframe.to_csv("EventBrite_Data2.csv",index=False)

