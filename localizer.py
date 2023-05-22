# from geopy.geocoders import Nominatim
# from functools import partial
#
#
# geolocator = Nominatim(user_agent="Bing Maps")
# geocode = partial(geolocator.geocode, language="en")


# country_list = []
aoi = []


def country_zone_finder(df, list_of_interest):
    for country in df['country']:
        # country_name = str(geocode(city)).split(",")[-1].strip(" ")
        # print(country_name)
        # country_list.append(country_name)
        if country in list_of_interest:
            aoi.append(1)
        else:
            aoi.append(0)
    # df['country'] = country_list
    df['aoi'] = aoi

    return df
