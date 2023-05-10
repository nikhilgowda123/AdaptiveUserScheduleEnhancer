from bs4 import BeautifulSoup
import requests
import pandas as pd
Activity_url_dict=dict()
Activity_url_dict['Activites']="https://www.tripadvisor.ie/Attractions-g186605-Activities-oa%s-Dublin_County_Dublin.html"
Activity_url_dict['Tours']="https://www.tripadvisor.ie/Attractions-g186605-Activities-c42-oa%s-Dublin_County_Dublin.html"
Activity_url_dict['DayTrips']="https://www.tripadvisor.ie/Attractions-g186605-Activities-c63-oa%s-Dublin_County_Dublin.html"
Activity_url_dict['OutdoorActivites']="https://www.tripadvisor.ie/Attractions-g186605-Activities-c61-Dublin_County_Dublin.html"
Activity_url_dict['Theatre_and_Concerts']="https://www.tripadvisor.ie/Attractions-g186605-Activities-c58-Dublin_County_Dublin.html"
Activity_url_dict['Food & Wine']="https://www.tripadvisor.ie/Attractions-g186605-Activities-c36-oa%s-Dublin_County_Dublin.html"
Activity_url_dict['Events']="https://www.tripadvisor.ie/Attractions-g186605-Activities-c62-Dublin_County_Dublin.html"
Activity_url_dict['Shopping']="https://www.tripadvisor.ie/Attractions-g186605-Activities-c26-oa%s-Dublin_County_Dublin.html"
Activity_url_dict['Transport']="https://www.tripadvisor.ie/Attractions-g186605-Activities-c59-oa%s-Dublin_County_Dublin.html"
Activity_url_dict['Traveller Resources']="https://www.tripadvisor.ie/Attractions-g186605-Activities-c60-oa%s-Dublin_County_Dublin.html"
consolidated_dataframe_1 = pd.DataFrame()
for keys in Activity_url_dict.keys():
    consolidated_dataframe = pd.DataFrame()
    main_url = Activity_url_dict[keys]
    if (main_url.__contains__("%s")):
        main_url = main_url % (0)
        res = requests.get(main_url, headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})
        soup = BeautifulSoup(res.content, 'html.parser')
        total_text = soup.find('div', class_="Ci").text
        print(total_text)
        numbers = total_text.split("-")[1].split("of")
        last_no = int(numbers[0].replace(",", ""))
        total_no = int(numbers[1].replace(",", ""))
    else:
        last_no = 2
        total_no = 2
    i = 0
    while i < total_no:
        details_list = []
        if (Activity_url_dict[keys].__contains__("%s")):
            url = Activity_url_dict[keys] % (i)
        else:
            url = Activity_url_dict[keys]
        print(url)
        res = requests.get(url, headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        soup = BeautifulSoup(res.content, 'html.parser')
        names_list = soup.find_all('span', class_='title')
        fares = soup.find_all('div', class_='biGQs _P fiohW avBIb ngXxk')
        extra_tip_details = soup.find_all('div', class_='dxkoL')
        Type_of_trip = extra_tip_details[0].find('div', class_='biGQs _P pZUbB hmDzD').text
        desciptions = soup.find_all('span', class_='SwTtt')
        trip_cards = soup.find_all('div', class_='hZuqH')
        duration_of_trips = soup.find_all('div', class_='bRMrl _Y K fOSqw')
        pre_links = soup.find_all('div', class_='alPVI eNNhq PgLKC tnGGX')
        for index in range(len(names_list)):
            details_dict = dict()
            details_dict['EventName'] = names_list[index].text
            if (fares):
                try:
                    details_dict['Fare'] = fares[index].text
                except:
                    details_dict['Fare'] = ""
            else:
                details_dict['Fare'] = ""
            if extra_tip_details:
                details_dict['TypeOfTrip'] = extra_tip_details[index].find('div', class_='biGQs _P pZUbB hmDzD').text
            else:
                details_dict['TypeOfTrip'] = ""
                details_dict['DurationOfTrip'] = duration_of_trips[index].text if duration_of_trips else ''
            rating_card = trip_cards[index].find('svg', class_='UctUV d H0 hzzSG')
            ratings_words = "0.0"
            if (rating_card):
                ratings_words = rating_card['aria-label']
                ratings_words = ratings_words.split("of")[0]
                details_dict['Ratings'] = ratings_words
            else:
                details_dict['Ratings'] = ratings_words
            try:
                details_dict['description'] = desciptions[index].text if desciptions else ''
            except:
                details_dict['description'] = ''
            link = pre_links[index].find('a', href=True)
            details_dict['Link'] = ('https://www.tripadvisor.ie' + link['href'])
            details_list.append(details_dict)
        df = pd.DataFrame(details_list)
        consolidated_dataframe = pd.concat([consolidated_dataframe, df])
        if soup.find('div', class_="Ci"):
            total_text = soup.find('div', class_="Ci").text
            numbers = total_text.split("-")[1].split("of")
            last_no = int(numbers[0].replace(",", ""))
            total_no = int(numbers[1].replace(",", ""))

        else:
            last_no = 2
            total_no = 2
        i = last_no
        consolidated_dataframe['Event_Type'] = keys
    consolidated_dataframe_1 = pd.concat([consolidated_dataframe_1, consolidated_dataframe])
consolidated_dataframe_1.drop_duplicates(inplace=True)
consolidated_dataframe_1.to_csv("TripAdvisorData.csv",index=False)