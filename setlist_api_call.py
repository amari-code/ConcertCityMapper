import requests
import pandas as pd
from secret_id import setlistapikeyv
from datetime import datetime


current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")
setlistapikey = setlistapikeyv[1]
headerssetlist = {
    "x-api-key": setlistapikey,
    "Accept": 'application/json'
}

headersMusicBrainz = {
    "Accept": 'application/json',
}


# test

# artist_query = "Verdena"

def artist_query(artists):
    global temp_dict, art_arr
    count = 1
    len_art = len(artists)
    city_name = []
    city_lat = []
    city_long = []
    # city_venue = []
    event_date = []
    artist_list = []
    country = []
    loi = []
    for artist in artists:
        print(str(count) + "/" + str(len_art) + " " + artist)
        responsemusicbrainz = requests.get(" https://musicbrainz.org/ws/2/artist/?query=" + artist,
                                           headers=headersMusicBrainz)

        # print(responsemusicbrainz.status_code)
        res = (responsemusicbrainz.json())
        # print('Res: ', (res['artists'])[0]['id'])
        mbid = res['artists'][0]['id']

        responsesetlist1 = requests.get("https://api.setlist.fm/rest/1.0/artist/"+mbid+"/setlists?p=1",
                                        headers=headerssetlist)
        responsesetlist2 = requests.get("https://api.setlist.fm/rest/1.0/artist/"+mbid+"/setlists?p=2",
                                        headers=headerssetlist)
        responsesetlist_list = [responsesetlist1]#, responsesetlist2]

        #
        # print(responsesetlist1.json())

        try:
            for responsesetlist in responsesetlist_list:
                # print(responsesetlist.status_code)
                for line in responsesetlist.json()['setlist']:
                    # print(responsesetlist.json()['setlist'])
                    try:
                        # print(line)
                        temp_dict = {
                            "artist": artist,
                            "eventdate": line['eventDate'],
                            "name": str(line['venue']['city']['name']),
                            "long": line['venue']['city']['coords']['long'],
                            "lat": line['venue']['city']['coords']['lat'],
                            "country": line['venue']['city']['country']['name'],
                            # "venue": city_venue

                        }
                        # artist_list.append(artist)
                        # event_date_var = (line['eventDate'])
                        # city_name_var = (line['venue']['city']['name'])
                        # city_lat_var = (line['venue']['city']['coords']['lat'])
                        # city_long_var = (line['venue']['city']['coords']['long'])
                        # city_venue_var = (line['venue']['name'])
                    except KeyError as ke:
                        print(ke)
                        temp_dict[ke] = None
                        continue
                        # city_venue.append(line['venue']['name'])
                    artist_list.append(temp_dict["artist"])
                    city_name.append(temp_dict["name"])
                    city_lat.append(temp_dict["lat"])
                    city_long.append(temp_dict["long"])
                    # city_venue.append(temp_dict[ke])
                    event_date.append(temp_dict["eventdate"])
                    country.append(temp_dict["country"])
                    # country.append(country_name)
                    # if country_name in list_of_interest:
                    #     loi.append(1)
                    # else:
                    #     loi.append(0)
        except KeyError as e:
            print(e)
            continue
            # print("City name: ", city_name)

        art_arr = pd.DataFrame(
            {
                "artist": artist_list,
                "date": event_date,
                "city_name": city_name,
                "city_long": city_lat,
                "city_lat": city_long,
                "country": country,
                # "loi": loi
                # "venue": city_venue
            }
        )
        count += 1
        # current_time = datetime.datetime.now()
        # time_stamp = current_time.timestamp()
        # date_time = datetime.fromtimestamp(time_stamp)
        # str_date_time = date_time.strftime("%d-%m-%Y_%H:%M:%S")
        art_arr.to_csv("lists/list" + current_timestamp + ".csv")

    # print(art_arr)
    # art_arr.append(art_arr)
    return art_arr

    # art_frame.append(art_arr)
# print((art_arr.to_string()))


# df = pd.read_json(text)
#
# print(df.to_string())