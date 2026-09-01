import joblib
import pandas as pd

MODEL_PATH = "soil_prediction_models.pkl"
SCALER_PATH = "soil_feature_scaler.pkl"
LEVEL_PATH = "soil_level_encoders.pkl"

soil_models = joblib.load(MODEL_PATH)
soil_scaler = joblib.load(SCALER_PATH)
soil_encoders = joblib.load(LEVEL_PATH)

soil_levels = list(soil_models.keys())

city_data = pd.read_csv("lat_lon_city.csv")


def city_to_lat_long(city):
    lat_lon = city_data.loc[
        city_data["City"].str.lower() == city.strip().lower(),
        ["Latitude", "Longitude"]
    ]

    if lat_lon.empty:
        raise ValueError(f"City '{city}' not found")

    latitude = float(lat_lon.iloc[0]["Latitude"])
    longitude = float(lat_lon.iloc[0]["Longitude"])

    return latitude, longitude


def predict_soil_characteristics(city):
    latitude, longitude = city_to_lat_long(city)

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
