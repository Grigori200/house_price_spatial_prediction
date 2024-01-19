import requests
from geopy.distance import geodesic
import pandas as pd
from tqdm import tqdm


def calculate_distance(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    return geodesic(coord1, coord2).meters


def transform_list_of_dicts(input_list: list[dict[str, int]]) -> dict[str, list[int]]:
    result_dict = {}
    for dictionary in input_list:
        for key, value in dictionary.items():
            if key not in result_dict:
                result_dict[key] = []
            result_dict[key].append(value)

    return result_dict


def address2location(api_key: str, address: str) -> tuple[float, float]:
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    geocoding_params = {
        "address": address,
        "key": api_key,
    }

    geocoding_response = requests.get(geocoding_url, geocoding_params)
    geocoding_data = geocoding_response.json()

    if geocoding_response.status_code != 200 or geocoding_data.get("status") != "OK":
        raise Exception(f'{geocoding_response.status_code} | {geocoding_data.get("status")} | Cannot find coordinates for {address}')

    location = geocoding_data["results"][0]["geometry"]["location"]
    return location['lat'], location['lng']


def get_nearby_places(api_key: str, address: str, tags: list[str], radius: int = 1000) -> dict:
    results = dict()
    places_url = "https://places.googleapis.com/v1/places:searchNearby"

    try:
        lat, lng = address2location(api_key, address)
        results['address'] = address
        results['lat'] = lat
        results['lng'] = lng
    except Exception as e:
        print(e)
        return results

    params = {
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lng
                },
                "radius": radius
            }
        },
        "rankPreference": "DISTANCE"
    }
    headers = {
        "Content-Type": 'application/json',
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": 'places.location,places.rating'
    }

    for tag in tags:
        params["includedTypes"] = [tag]
        response = requests.post(places_url, json=params, headers=headers)
        data = response.json()
        places = data.get("places", [])
        places = list(filter(lambda place: place.get('rating', 0) > 0, places))
        shortest_path = None

        if places:
            nearest = places[0].get('location', dict())
            coords = nearest.get("latitude"), nearest.get("longitude")
            shortest_path = calculate_distance((lat, lng), coords)

        results[tag] = len(places)
        results[f'{tag}_closest'] = shortest_path

    return results


if __name__ == "__main__":
    API_KEY = 'your_key'
    types = ['store',
             'school',
             'university',
             'health',
             'park',
             'supermarket',
             'shopping_mall',
             'restaurant',
             'cafe',
             'gym',
             'church',
             'train_station',
             'transit_station']
    df = pd.read_csv('oto.csv', index_col=0)
    df = df.drop_duplicates('address')

    poi_df = pd.DataFrame(transform_list_of_dicts([
        get_nearby_places(API_KEY, row['address'], types)
        for _, row in tqdm(df.iterrows(), total=len(df.index))
    ]))
    out_df = pd.merge(df, poi_df, how='inner', on='address')
    out_df.to_csv('oto_points.csv', index=False)
