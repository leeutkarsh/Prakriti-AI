from soil import address_to_lat_long, predict_soil_characteristics
from weather_api import get_historical_weather, get_weather_forecast
from extract_features import extract_features

def flatten_weather_features(address, stp, isstp):
    dik = predict_soil_characteristics(address)

    lat, long = address_to_lat_long(address)
    fd, hd = get_weather_forecast(lat, long), get_historical_weather(lat, long)
    data = extract_features(forecast_data=fd, historical_data=hd)

    flattened = {}

    # Historical features
    for key, value in data["historical_features"].items():
        flattened[f"historical_{key}"] = value

    # Forecast features
    for key, value in data["forecast_features"].items():
        flattened[f"forecast_{key}"] = value

    flattened["Soil_Type"] = stp
    flattened["N_level"] = dik["N_level"]
    flattened["P_level"] = dik["P_level"]
    flattened["K_level"] = dik["K_level"]
    flattened["Ph_level"] = dik["pH_level"]
    flattened["Issue_type"] = isstp

    return flattened

def temp_humid(address):
    dik = predict_soil_characteristics(address)
    lat, long = address_to_lat_long(address)
    data = get_weather_forecast(lat, long)
    temp = 'temperature_2m'
    hum = 'relative_humidity_2m'
    return data["hourly"][temp][0], data["hourly"][hum][0]

def other(address):
    lat, long = address_to_lat_long(address)
    data = get_weather_forecast(lat, long)
    soil_mois = 'soil_moisture_0_to_1cm'
    soil_temp = 'soil_temperature_0cm'
    rainfall = 'rain'
    unito = {
    'temperature_2m': '°C',
    'relative_humidity_2m': '%',
    'soil_temperature_0cm': '°C',
    'soil_moisture_0_to_1cm': 'm³/m³',
    'rain': 'mm'
}
    return (data["hourly"][soil_temp][0],
            data["hourly"][soil_mois][0],
            data["hourly"][rainfall][0],
            unito)