#!/usr/bin/env python3

from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import requests
import os
import spotipy
import pandas as pd
import matplotlib.pyplot as plt

__author__ = "Antonio Mariano"
__copyright__ = "Copyright 2023, ConcertCityMapper"
__license__ = "MPL 2."
__version__ = "0.1.0"
__email__ = "a_mariano@live.it"
__status__ = "Prototype"


class Mapper:

    def __init__(self, spotify_client_id, spotify_client_secret, setlist_api_key):

        self.artist_list_from_spotify = []
        self.artist_list_from_setlist = pd.DataFrame()
        self.SPOTIPY_CLIENT_ID = spotify_client_id
        self.SPOTIPY_CLIENT_SECRET = spotify_client_secret
        self.setlist_api_key = setlist_api_key
        # list of country to filter data
        self.list_of_interest = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark",
                                 "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
                                 "Latvia", "Lithuania", "Luxembourg", "Malta", "The Netherlands", "Poland", "Portugal",
                                 "Romania", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Netherlands",
                                 "Czechia"]

    # retrieve artist setlists data from setlist.fm APIs
    def artist_query(self, lim=-1):
        current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")
        temp_dict = {}
        count = 1
        len_art = len(self.artist_list_from_spotify)
        city_name = []
        city_lat = []
        city_long = []
        event_date = []
        artist_name = []
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

        for artist in self.artist_list_from_spotify[:end]:
            print(str(count) + "/" + str(end) + " " + artist)
            # retrieve the artist musicbrainz id required by setlist.fm (to avoid mistake when artists have same names)
            response_music_brainz = requests.get(" https://musicbrainz.org/ws/2/artist/?query=" + artist,
                                                 headers=headers_musicbrainz)

            res = (response_music_brainz.json())

            try:
                music_brainz_id = res['artists'][0]['id']  # musicbrainz id
            except KeyError as e:
                print(str(e) + " not available")
                continue
            # retrieve first page of artist setlists. More can be retrieved and added to response_setlist_list
            response_setlist_p1 = requests.get("https://api.setlist.fm/rest/1.0/artist/" + music_brainz_id + 
                                               "/setlists?p=1",
                                               headers=headers_setlist
                                               )
            
            # this is left as a list in case more pages from the APIs are retrieved
            response_setlist_list = [response_setlist_p1]  
            try:
                for response_setlist in response_setlist_list:

                    for line in response_setlist.json()['setlist']:
                        try:
                            temp_dict = {
                                "artist": artist,
                                "event_date": line['eventDate'],
                                "name": str(line['venue']['city']['name']),
                                "long": line['venue']['city']['coords']['long'],
                                "lat": line['venue']['city']['coords']['lat'],
                                "country": line['venue']['city']['country']['name'],

                            }
                        except KeyError as ke:
                            print(str(ke) + " not available")
                            temp_dict[ke] = None
                            continue

                        artist_name.append(temp_dict["artist"])
                        city_name.append(temp_dict["name"])
                        city_lat.append(temp_dict["lat"])
                        city_long.append(temp_dict["long"])
                        event_date.append(temp_dict["event_date"])
                        country.append(temp_dict["country"])
            except KeyError as e:
                print(str(e) + " not available")
                continue

            self.artist_list_from_setlist = pd.DataFrame(
                {
                    "artist": artist_name,
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
            # temporary backup csv file to avoid losing data if the connection to setlist fall
            self.artist_list_from_setlist.to_csv("temp_list/list" + current_timestamp + ".csv")

    # retrieve favourite artists from Spotify APIs
    def spotify_query(self):

        last_id = None

        count = 0
        # Spotify authorization request
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.SPOTIPY_CLIENT_ID,
                                                       client_secret=self.SPOTIPY_CLIENT_SECRET,
                                                       redirect_uri="http://localhost:7777/callback",
                                                       scope="user-follow-read"))

        # retrieve artists in blocks of 50
        while True:
            results = sp.current_user_followed_artists(limit=50, after=last_id)
            for artist in results['artists']['items']:
                self.artist_list_from_spotify.append(artist['name'])
                last_id = artist['id']
                count += 1
            if results['artists']['next'] is None:
                break

    # routine that flag the country if they're in list_of_interest
    def country_zone_finder(self):
        aoi = []
        for country in self.artist_list_from_setlist['country']:

            if country in self.list_of_interest:
                aoi.append(1)
            else:
                aoi.append(0)

        self.artist_list_from_setlist['aoi'] = aoi

    # format and filter the dataframe before plotting
    @staticmethod
    def plot_filter(df, min_occ=5):
        eu_cities = df[df["aoi"] == 1]
        eu_cities['date'] = pd.to_datetime(eu_cities['date'], format='%d-%m-%Y')
        eu_cities_2 = eu_cities[eu_cities["date"] > '01-01-2020']
        eu_cities_count = eu_cities_2['city_name'].value_counts()
        eu_filter = eu_cities_count[eu_cities_count > min_occ].sort_values()
        eu_filter.plot.barh()
        for a in range(len(eu_filter)):
            plt.text(eu_filter[a] / 2, a, eu_filter[a], color='white')
        plt.title("Concerts distribution by favourite bands")
        plt.xlabel("Number of concerts")
        plt.ylabel("Cities")
        plt.show()
        plt.close('all')
