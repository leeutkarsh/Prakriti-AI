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
        "forecast_days": 1,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m"
        ],
        "timezone": "auto"
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    # Example: City(Bhopal)
    latitude = 23.2599
    longitude = 77.4126

    weather = get_weather_forecast(latitude, longitude)

    print(weather)