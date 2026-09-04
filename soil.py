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

def get_coordinates(address):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "Prakriti-AI/1.0"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            raise ValueError(f"Could not find coordinates for: {address}")

        return data[0]

    except requests.exceptions.Timeout:
        raise ConnectionError(
            "Location service timed out. Please check your internet connection "
            "and try again."
        )

    except requests.exceptions.RequestException as e:
        raise ConnectionError(
            f"Location service request failed: {e}"
        )


def address_to_lat_long(address):
    location = get_coordinates(address)

    if location is None:
        raise ValueError(f"Location not found: {address}")

    return location["lat"], location["lon"]


def predict_soil_characteristics(address):
    latitude, longitude = address_to_lat_long(address)

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

    for i, k in predictions.items():
        if k == "Medium" or k == "Neutral":
            predictions[i] = "Mid"

    return predictions