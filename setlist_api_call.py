import requests
import pandas as pd
from secret_id import setlistapikeyv
from datetime import datetime
import os


current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")
setlistapikey = setlistapikeyv[1]
headerssetlist = {
    "x-api-key": setlistapikey,
    "Accept": 'application/json'
}

headersMusicBrainz = {
    "Accept": 'application/json',
}


def artist_query(artists):
    global temp_dict, art_arr
    count = 1
    len_art = len(artists)
    city_name = []
    city_lat = []
    city_long = []
    event_date = []
    artist_list = []
    country = []
    for artist in artists:
        print(str(count) + "/" + str(len_art) + " " + artist)
        responsemusicbrainz = requests.get(" https://musicbrainz.org/ws/2/artist/?query=" + artist,
                                           headers=headersMusicBrainz)

        res = (responsemusicbrainz.json())

        try:
            mbid = res['artists'][0]['id']
        except KeyError as e:
            print(str(e) + " not available")
            continue

        responsesetlist1 = requests.get("https://api.setlist.fm/rest/1.0/artist/"+mbid+"/setlists?p=1",
                                        headers=headerssetlist)
        responsesetlist_list = [responsesetlist1]
        try:
            for responsesetlist in responsesetlist_list:

                for line in responsesetlist.json()['setlist']:
                    try:
                        temp_dict = {
                            "artist": artist,
                            "eventdate": line['eventDate'],
                            "name": str(line['venue']['city']['name']),
                            "long": line['venue']['city']['coords']['long'],
                            "lat": line['venue']['city']['coords']['lat'],
                            "country": line['venue']['city']['country']['name'],

                        }
                    except KeyError as ke:
                        print(str(ke) + " not available")
                        temp_dict[ke] = None
                        continue

                    artist_list.append(temp_dict["artist"])
                    city_name.append(temp_dict["name"])
                    city_lat.append(temp_dict["lat"])
                    city_long.append(temp_dict["long"])
                    event_date.append(temp_dict["eventdate"])
                    country.append(temp_dict["country"])
        except KeyError as e:
            print(str(e) + " not available")
            continue

        art_arr = pd.DataFrame(
            {
                "artist": artist_list,
                "date": event_date,
                "city_name": city_name,
                "city_long": city_lat,
                "city_lat": city_long,
                "country": country,
            }
        )
        count += 1
        try:
            os.mkdir(os.getcwd() + '/temp_list')
        except FileExistsError:
            pass
        art_arr.to_csv("temp_list/list" + current_timestamp + ".csv")

    return art_arr
