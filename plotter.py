import pandas as pd
import localizer
import datetime
df = pd.read_csv("/Users/antoniomariano/PycharmProjects/ConcertCityMapper/list_final_180402300323.csv")

list_of_interest = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
                    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania",
                    "Luxembourg", "Malta", "The Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
                    "Spain", "Sweden", "Switzerland", "Netherlands", "Czechia"]

def plot_bar(df, min_occ=30):
    dataf = localizer.country_zone_finder(df, list_of_interest)
    eu_cities = dataf[dataf["aoi"] == 1]
    eu_cities['date'] = pd.to_datetime(eu_cities['date'], format='%d-%m-%Y')
    eu_cities_2 = eu_cities[eu_cities["date"] > '01-01-2020']
    # print(type(eu_cities))
    print(eu_cities_2)
    # a = eu_cities[(eu_cities.eu_neu == "Europe")]
    # print(type(a))
    eu_cities_count = eu_cities_2['city_name'].value_counts()
    # print(type(eu_cities_count))
    # print(eu_cities_count)
    eu_filt = eu_cities_count[eu_cities_count > min_occ].sort_values()
    # print(type(eu_filt))
    # print(eu_filt)
    eu_filt.plot.barh()


plot_bar(df, 10)


