import pylab as pl
import requests
import pandas as pd
from datetime import datetime
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import localizer
import matplotlib.pyplot as plt


class Mapper:

    def __init__(self, spotify_client_id, spotify_client_secret, setlist_apikeyv):

        self.artist_list = []
        self.art_arr = []
        self.SPOTIPY_CLIENT_ID = spotify_client_id
        self.SPOTIPY_CLIENT_SECRET = spotify_client_secret
        self.current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")
        self.setlist_api_key = setlist_apikeyv
        self.list_of_interest = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
                    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania",
                    "Luxembourg", "Malta", "The Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
                    "Spain", "Sweden", "Switzerland", "Netherlands", "Czechia"]

    def artist_query(self, lim = -1):
        temp_dict = {}
        count = 1
        len_art = len(self.artist_list)
        city_name = []
        city_lat = []
        city_long = []
        event_date = []
        artist_list = []
        country = []

        headers_setlist = {
            "x-api-key": self.setlist_api_key,
            "Accept": 'application/json'
        }

        headers_musicbrainz = {
            "Accept": 'application/json',
        }

        if lim == -1:
            end = len_art
        else:
            end = lim

        for artist in self.artist_list[:end]:
            print(str(count) + "/" + str(end) + " " + artist)
            response_music_brainz = requests.get(" https://musicbrainz.org/ws/2/artist/?query=" + artist,
                                               headers=headers_musicbrainz)

            res = (response_music_brainz.json())

            try:
                mbid = res['artists'][0]['id']
            except KeyError as e:
                print(str(e) + " not available")
                continue

            response_setlist1 = requests.get("https://api.setlist.fm/rest/1.0/artist/" + mbid + "/setlists?p=1",
                                            headers=headers_setlist)
            response_setlist_list = [response_setlist1]
            try:
                for response_setlist in response_setlist_list:

                    for line in response_setlist.json()['setlist']:
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

            self.art_arr = pd.DataFrame(
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
            self.art_arr.to_csv("temp_list/list" + self.current_timestamp + ".csv")

        # return art_arr

    def spotify_query(self):

        last_id = None

        count = 0
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.SPOTIPY_CLIENT_ID,
                                                       client_secret=self.SPOTIPY_CLIENT_SECRET,
                                                       redirect_uri="http://localhost:7777/callback",
                                                       scope="user-follow-read"))

        while True:
            results = sp.current_user_followed_artists(limit=50, after=last_id)
            for artist in results['artists']['items']:
                self.artist_list.append(artist['name'])
                last_id = artist['id']
                count += 1
            if results['artists']['next'] is None:
                break

    def country_zone_finder(self):
        aoi = []
        for country in self.art_arr['country']:

            if country in self.list_of_interest:
                aoi.append(1)
            else:
                aoi.append(0)

        self.art_arr['aoi'] = aoi

        # return df

    def plot_filt(self, df, min_occ=5):
        dataf = localizer.country_zone_finder(df, self.list_of_interest)
        eu_cities = dataf[dataf["aoi"] == 1]
        eu_cities['date'] = pd.to_datetime(eu_cities['date'], format='%d-%m-%Y')
        eu_cities_2 = eu_cities[eu_cities["date"] > '01-01-2020']
        eu_cities_count = eu_cities_2['city_name'].value_counts()
        eu_filt = eu_cities_count[eu_cities_count > min_occ].sort_values()
        eu_filt.plot.barh()
        for a in range(len(eu_filt)):
            plt.text(eu_filt[a]/2, a-0.15, eu_filt[a], color='white')
        plt.title("Concerts distribution by favourite bands")
        plt.xlabel("Number of concerts")
        plt.ylabel("Cities")
        plt.show()
        plt.close('all')
