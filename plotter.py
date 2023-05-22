import pandas as pd
import localizer
import matplotlib.pyplot as plt
import time

# df = pd.read_csv("/Users/antoniomariano/PycharmProjects/ConcertCityMapper/list_final_104932220523.csv")
#
# list_of_interest = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
#                     "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania",
#                     "Luxembourg", "Malta", "The Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
#                     "Spain", "Sweden", "Switzerland", "Netherlands", "Czechia"]

def plot_filt(df, list_of_interest, min_occ=5):
    dataf = localizer.country_zone_finder(df, list_of_interest)
    eu_cities = dataf[dataf["aoi"] == 1]
    eu_cities['date'] = pd.to_datetime(eu_cities['date'], format='%d-%m-%Y')
    eu_cities_2 = eu_cities[eu_cities["date"] > '01-01-2020']
    print(eu_cities_2)
    eu_cities_count = eu_cities_2['city_name'].value_counts()
    eu_filt = eu_cities_count[eu_cities_count > min_occ].sort_values()
    print(eu_filt)
    eu_filt.plot.barh()
    plt.title("Concerts distribution by favourite bands")
    plt.xlabel("Number of concerts")
    plt.ylabel("Cities")
    # plt.barh(eu_filt, eu_filt, tick_label = eu_filt['city_name'] )
    plt.show()
    plt.close('all')


# plot_filt(df, list_of_interest)

