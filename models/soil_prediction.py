import joblib
import pandas as pd
import requests

MODEL_PATH = "soil_prediction_models.pkl"
SCALER_PATH = "soil_feature_scaler.pkl"
LEVEL_PATH = "soil_level_encoders.pkl"

soil_models = joblib.load(MODEL_PATH)
soil_scaler = joblib.load(SCALER_PATH)
soil_encoders = joblib.load(LEVEL_PATH)

soil_levels = list(soil_models.keys())

def get_coordinates(location):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": location,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "in"
    }

    headers = {
        "User-Agent": "SIH-Agriculture"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    return {
        "latitude": float(data[0]["lat"]),
        "longitude": float(data[0]["lon"]),
        "display_name": data[0]["display_name"]
    }


def address_to_lat_long(address):
    location = get_coordinates(address)

    if location is None:
        raise ValueError(f"Location not found: {address}")

    return location["latitude"], location["longitude"]


def predict_soil_characteristics(address):
    latitude, longitude = address_to_lat_long(address)

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")

    input_location = pd.DataFrame(
        [[latitude, longitude]],
        columns=["Latitude", "Longitude"]
    )

    input_scaled = soil_scaler.transform(input_location)

    predictions = {}

    for level in soil_levels:
        encoded_prediction = soil_models[level].predict(
            input_scaled
        )[0]

        predicted_level = soil_encoders[level].inverse_transform(
            [int(encoded_prediction)]
        )[0]

        predictions[level] = predicted_level

    return predictions
