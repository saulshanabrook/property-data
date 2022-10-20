import os
import pickle

import googlemaps

__all__ = ["add_directions_columns"]



def add_directions_columns(df):
    """
    Adds duration (minutes) and a distance (kms) columns to the dataframe, using the
    distance matrix API.
    """
    lat_longs = df.geometry.centroid.to_crs("EPSG:4326").apply(lambda pt: (pt.y, pt.x))
    results = fetch_data(lat_longs)
    duration = [r['duration']['value'] / 60 for r in results]
    distance = [r['distance']['value'] / 1000 for r in results]
    return df.assign(duration=duration, distance=distance)



def fetch_data(lat_longs):
    """
    Fetch data, using the cached values if possible. Returns a list of results.
    """
    gmaps = googlemaps.Client(key=os.environ["GOOGLE_MAPS_API_KEY"])
    data = load_data()
    unfetched_lat_longs = [lat_long for lat_long in lat_longs if lat_long not in data]
    for group in chunker(unfetched_lat_longs, 20):
        results = gmaps.distance_matrix((42.58774713218186, -72.60008261544128), group, mode='driving')
        for lat_long, element in zip(group, results['rows'][0]['elements']):
            data[lat_long] = element
    save_data(data)
    return [data[lat_long] for lat_long in lat_longs]
    




def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))



def load_data():
    with open('distance_data.pickle', 'rb') as f:
        return pickle.load(f)

def save_data(data):
    with open('distance_data.pickle', 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
