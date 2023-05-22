def country_zone_finder(df, list_of_interest):
    aoi = []
    for country in df['country']:

        if country in list_of_interest:
            aoi.append(1)
        else:
            aoi.append(0)

    df['aoi'] = aoi

    return df
