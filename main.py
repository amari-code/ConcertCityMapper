import setlist_api_call as setlist
import spotify_api_connect as spot
from datetime import datetime
import localizer
import plotter

current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")

print(spot.artist_list)

data = setlist.artist_query(spot.artist_list)

data_final = localizer.country_zone_finder(data)

data_final.to_csv("list_final_"+current_timestamp+".csv")

plotter.plot_bar(data, min_occ=0)

