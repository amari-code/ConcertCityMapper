#!/usr/bin/env python3

from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import requests
import os
import spotipy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
from decouple import config
import json
import pprint

from bs4 import BeautifulSoup
import urllib.request
import ssl
import re
from unidecode import unidecode

import cufflinks as cf
import chart_studio.plotly as py
import chart_studio.tools as tls
import plotly.graph_objs as go

__author__ = "Antonio Mariano"
__copyright__ = "Copyright 2023, ConcertCityMapper"
__license__ = "MPL 2."
__version__ = "0.1.0"
__email__ = "a_mariano@live.it"
__status__ = "Prototype"

tls.set_credentials_file(username=config('plotly_username'), api_key=config('plotly_api_key'))
pd.options.plotting.backend = "plotly"
flags = re.IGNORECASE | re.MULTILINE
class Mapper:

    def __init__(self, spotify_client_id, spotify_client_secret, setlist_api_key):

        self.artist_list_from_spotify = []
        self.artist_list_from_songkick = pd.DataFrame()
        self.SPOTIPY_CLIENT_ID = spotify_client_id
        self.SPOTIPY_CLIENT_SECRET = spotify_client_secret
        self.setlist_api_key = setlist_api_key
        # list of country to filter data
        self.list_of_interest = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark",
                                 "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
                                 "Latvia", "Lithuania", "Luxembourg", "Malta", "The Netherlands", "Poland", "Portugal",
                                 "Romania", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Netherlands",
                                 "Czechia"]

        pd.set_option('display.max_columns', None)
        self.region_dataframe = pd.read_json('all.json')


    # scrape concert data from songkick
    def songkick_data_scraping(self, lim=-1, start_year=datetime.now().year):
        current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")
        count = 1
        len_art = len(self.artist_list_from_spotify)
        city_name = []
        event_date = []
        artist_name = []
        country = []
        event_venue = []
        region = []
        sub_region = []

        context = ssl._create_unverified_context()

        if lim == -1:
            end = len_art
        else:
            end = lim

        for artist in self.artist_list_from_spotify[:end]:

            print(f'{artist} : {count} of {end}')
            artist_to_query = artist.lower()
            url = f'https://www.songkick.com/search?page=1&per_page=10&query={urllib.parse.quote(artist_to_query)}&type=artists'
            artist_query = urllib.request.urlopen(url, context=context).read()
            soup = BeautifulSoup(artist_query, 'html.parser')

            actual_artist_list = soup.findAll('p', attrs={'class' : 'summary'})
            gigography_url = ''
            for actual_artist in actual_artist_list:
                if actual_artist.strong.string.lower().replace("'", " ") == artist_to_query:

                    actual_artist_url = actual_artist.a['href']
                    gigography_url = f'https://www.songkick.com{actual_artist_url}/gigography'
                    print(gigography_url)

                    break
                else:
                    continue

            try:
                while len(gigography_url) > 0:

                    gigs = urllib.request.urlopen(gigography_url, context=context).read()
                    gigography_event_listing = BeautifulSoup(gigs, 'html.parser')
                    try:
                        gigography_list = gigography_event_listing.findAll('ul', attrs={'class': re.compile("event-listings")})[0]
                    except IndexError:
                        raise StopIteration

                    gig_list = gigography_list.findAll('script', attrs={'type': 'application/ld+json'})

                    for gig in gig_list:

                        location_infos = json.loads(gig.string)[0]

                        try:
                            concert_date = location_infos['endDate']
                            concert_venue = location_infos['location']['name']
                            concert_city = location_infos['location']['address']['addressLocality']
                            concert_country = location_infos['location']['address']['addressCountry']

                        except AttributeError as ae:
                            # print(gig_infos)
                            print(ae)
                            continue
                        except KeyError as ke:
                            print(location_infos['location'])
                            print(ke)
                            continue

                        country_regions = self.region_dataframe[
                            (self.region_dataframe['name'].str.match(fr'.*\b{concert_country}\b.*',
                                                                     flags=flags)) |
                            (self.region_dataframe['alpha-2'].str.match(fr'.*\b{concert_country}\b.*',
                                                                        flags=flags))]

                        country_region = country_regions['region'].values[0]
                        country_sub_region = country_regions['sub-region'].values[0]

                        if datetime.strptime(concert_date, '%Y-%m-%d').year < start_year:
                            raise StopIteration

                        artist_name.append(artist)
                        event_date.append(concert_date)
                        event_venue.append(concert_venue)
                        city_name.append(concert_city)
                        country.append(concert_country)
                        region.append(country_region)
                        sub_region.append(country_sub_region)

                    try:

                        gigography_next_url = gigography_event_listing.findAll('a', attrs={'rel': re.compile("next")})[0]['href']
                        gigography_url = f'https://www.songkick.com{gigography_next_url}'
                    except IndexError as e:
                        print(e)
                        gigography_url = ''
            except StopIteration:
                pass

            count += 1

        self.artist_list_from_songkick = pd.DataFrame(
            {
                "artist": artist_name,
                "date": event_date,
                "event_venue": event_venue,
                "city_name": city_name,
                "country": country,
                "region": region,
                "sub_region": sub_region,
            }
        )

        try:
            os.mkdir(os.getcwd() + '/temp_list')
        except FileExistsError:
            pass
        # temporary backup csv file to avoid losing data if the connection to setlist fall
        self.artist_list_from_songkick.to_csv("temp_list/list" + current_timestamp + ".csv")

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

    # format and filter the dataframe before plotting
    @staticmethod
    def plot_filter(df, min_occ=10, year=datetime.now().year, region_filter=[], exclude_countries=[]):

        if region_filter:
            df1= pd.DataFrame()
            for region in region_filter:
                df1 = df1._append(df[(df['region'] == region) | (df['sub_region'] == region)])
            df = df1

        if exclude_countries:

            i=0
            for country in exclude_countries:
                df = (df[~(df['country'] == country)])
                i += 1

        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df[df["date"] > f'{year}-01-01']
        cities_count = df['city_name'].value_counts()
        print(cities_count)
        final = cities_count[cities_count > min_occ].sort_values(ascending=False)
        pal = sb.dark_palette('red', len(final), reverse=True)
        sb.barplot(x=final.values, y=final.index, orient='h', palette=pal)
        for a in range(len(final)):
            plt.text(final[a] / 2, a, final[a], color='white')
        plt.title("Concerts distribution by favourite bands")
        plt.xlabel("Number of concerts")
        plt.ylabel("Cities")
        plt.show()
        plt.savefig('city_dist.png')
        plt.close('all')
