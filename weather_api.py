import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_forecast(latitude, longitude):
    """
    Get up to 16 days of weather forecast for a location.

    Parameters:
        latitude (float): Location latitude.
        longitude (float): Location longitude.

    Returns:
        dict: JSON-compatible weather forecast data.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "forecast_days": 16,

        "hourly": [
            # Current weather
            "temperature_2m",
            "relative_humidity_2m",
            "dew_point_2m",
            "apparent_temperature",
            "precipitation",
            "cloud_cover",

            # Wind
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",

            # Visibility
            "visibility",

            # Soil
            "soil_temperature_0cm",
            "soil_moisture_0_to_1cm",

            # Agriculture / derived weather
            "vapour_pressure_deficit",
            "et0_fao_evapotranspiration",
            "evapotranspiration",
            "leaf_wetness_probability",

            # Solar
            "sunshine_duration",
            "shortwave_radiation",
            "uv_index",

            # Weather condition
            "weather_code"
        ],

        "timezone": "auto",

        # Units
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm"
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()

HISTORICAL_WEATHER_URL = OPEN_METEO_URL

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "precipitation",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "visibility",
    "soil_temperature_0cm",
    "soil_moisture_0_to_1cm",
    "vapour_pressure_deficit",
    "et0_fao_evapotranspiration",
    "evapotranspiration",
    "leaf_wetness_probability",
    "sunshine_duration",
    "shortwave_radiation",
    "uv_index",
    "weather_code"
]


def get_historical_weather(latitude, longitude):
    """
    Get the previous 92 days of hourly weather data
    for a given location.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,

        # Previous 92 days
        "past_days": 92,

        "hourly": HOURLY_VARIABLES,

        "timezone": "auto",

        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm"
    }

    response = requests.get(
        HISTORICAL_WEATHER_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()
