import requests
from geopy.distance import geodesic
import pandas as pd
from tqdm import tqdm


def calculate_distance(coord1: tuple[int, int], coord2: tuple[int, int]) -> float:
    return geodesic(coord1, coord2).meters


def transform_list_of_dicts(input_list: list[dict[str, int]]) -> dict[str, list[int]]:
    result_dict = {}
    for dictionary in input_list:
        for key, value in dictionary.items():
            if key not in result_dict:
                result_dict[key] = []
            result_dict[key].append(value)

    return result_dict


def get_nearby_places(api_key: str, address: str, tags: list[str], radius: int = 500) -> dict:
    results = {}

    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    geocoding_params = {
        "address": address,
        "key": api_key,
    }

    geocoding_response = requests.get(geocoding_url, params=geocoding_params)
    geocoding_data = geocoding_response.json()

    if geocoding_response.status_code == 200 and geocoding_data.get("status") == "OK":
        location = geocoding_data["results"][0]["geometry"]["location"]
        lat, lng = location["lat"], location["lng"]
        results['lat'] = lat
        results['lng'] = lng
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        for type in tags:
            counts = 0
            closest = 1000
            places_params = {
                "key": api_key,
                "location": f"{lat},{lng}",
                "radius": radius,
                "types": type
            }

            places_response = requests.get(places_url, params=places_params)
            places_data = places_response.json()
            for place in places_data.get("results", []):
                location = place.get("geometry", {}).get("location", {})
                place_coord = (location.get("lat"), location.get("lng"))
                distance = calculate_distance((lat, lng), place_coord)
                rating = place.get("rating", 0)

                if rating > 0:
                    counts += 1
                    closest = min(closest, distance)
            results[type] = counts
            results[f'{type}_closest'] = closest
    else:
        print("Geocoding request failed.")

    return results


if __name__ == "__main__":
    api_key = 'your_key'
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

    out_df = pd.concat([df, pd.DataFrame(transform_list_of_dicts([
        get_nearby_places(api_key, row['address'], types)
        for _, row in tqdm(df.iterrows(), total=len(df.index))]))], axis=1)
    out_df.to_csv('oto_points.csv', index=False)
