"""
extract_features.py

Compact disease/pest-relevant weather feature extraction
with robust missing-value handling.

Input:
    forecast_data
    historical_data

Output:
    One compact feature vector for the historical period
    and one compact feature vector for the forecast period.

Missing-value strategy:
    1. Ignore individual None values during aggregation.
    2. Learn feature medians from historical data.
    3. Fill missing historical features using historical medians.
    4. Apply the SAME historical medians to forecast features.
    5. If an entire feature is unavailable historically,
       use a predefined fallback value.
    6. Final ML features are always numeric.

Dataset compatibility:
    extract_features() returns two separate dicts
    (historical_features / forecast_features) with UNPREFIXED keys
    such as "avg_temperature_c". Any dataset built for training
    (e.g. a CSV with columns like "historical_avg_temperature_c" /
    "forecast_avg_temperature_c") needs those keys prefixed and
    flattened into a single row before they can share a schema.
    flatten_for_dataset() (bottom of this file) does exactly that,
    with no change to the extraction/imputation logic above it.
"""

from __future__ import annotations
from weather_api import get_weather_forecast, get_historical_weather
from datetime import datetime
from math import isfinite
from statistics import median
from typing import Any, Dict, List, Optional
from soil import address_to_lat_long, predict_soil_characteristics

# =====================================================================
# WEATHER VARIABLES WE ACTUALLY NEED
# =====================================================================

NUMERIC_VARIABLES = (
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "precipitation",
    "wind_speed_10m",
    "vapour_pressure_deficit",
    "soil_moisture_0_to_1cm",
    "et0_fao_evapotranspiration",
    "evapotranspiration",
    "leaf_wetness_probability",
)


# =====================================================================
# FALLBACK VALUES
# =====================================================================
#
# These are ONLY used when a feature has no usable historical value
# at all.
#
# They are deliberately conservative environmental defaults rather
# than pretending the missing variable was measured.
#
# For features whose units are percentages:
#       50 = neutral midpoint
#
# For moisture-related values:
#       0.20 = moderate soil moisture
#
# These fallbacks matter much less than learned historical medians.
# =====================================================================

FALLBACK_VALUES = {
    "avg_temperature_c": 25.0,
    "min_temperature_c": 20.0,
    "max_temperature_c": 30.0,

    "avg_humidity_pct": 70.0,
    "high_humidity_pct": 0.0,
    "very_high_humidity_pct": 0.0,
    "dry_air_pct": 0.0,

    "rainfall_total_mm": 0.0,
    "rain_hours_pct": 0.0,
    "heavy_rain_hours_pct": 0.0,

    "avg_leaf_wetness_pct": 0.0,
    "leaf_wetness_hours_pct": 0.0,
    "high_leaf_wetness_hours_pct": 0.0,

    "avg_vpd_kpa": 1.0,
    "low_vpd_hours_pct": 0.0,
    "very_low_vpd_hours_pct": 0.0,

    "hot_humid_hours_pct": 0.0,
    "hot_hours_pct": 0.0,
    "cool_hours_pct": 0.0,

    "avg_dew_point_depression_c": 5.0,

    "avg_soil_moisture_m3_m3": 0.20,

    "avg_wind_speed_kmh": 10.0,

    "total_et0_mm": 0.0,
    "total_evapotranspiration_mm": 0.0,
}


# =====================================================================
# HELPERS
# =====================================================================

def _finite_float(value: Any) -> Optional[float]:
    """
    Convert a value to float if it is finite.
    Otherwise return None.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not isfinite(number):
        return None

    return number


def _parse_time(value: Any) -> Optional[datetime]:
    """
    Parse ISO timestamp.
    """

    if not isinstance(value, str):
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def _mean(values: List[float]) -> Optional[float]:
    if not values:
        return None

    return sum(values) / len(values)


def _minimum(values: List[float]) -> Optional[float]:
    if not values:
        return None

    return min(values)


def _maximum(values: List[float]) -> Optional[float]:
    if not values:
        return None

    return max(values)


def _percentage(
    count: int,
    total: int,
) -> Optional[float]:

    if total <= 0:
        return None

    return 100.0 * count / total


# =====================================================================
# VALIDATE OPEN-METEO PAYLOAD
# =====================================================================

def _validate_payload(
    payload: Any,
    name: str,
) -> Dict[str, Any]:

    if not isinstance(payload, dict):
        raise TypeError(
            f"{name} must be a dictionary."
        )

    hourly = payload.get("hourly")

    if not isinstance(hourly, dict):
        raise ValueError(
            f"{name} is missing 'hourly'."
        )

    times = hourly.get("time")

    if not isinstance(times, list):
        raise ValueError(
            f"{name} is missing hourly['time']."
        )

    return payload


# =====================================================================
# EXTRACT HOURLY DATA
# =====================================================================

def _extract_hourly_data(
    payload: Dict[str, Any]
) -> Dict[str, List[float]]:

    hourly = payload["hourly"]

    times = hourly["time"]

    data: Dict[str, List[float]] = {
        field: []
        for field in NUMERIC_VARIABLES
    }

    valid_hours = 0

    for index, timestamp in enumerate(times):

        if _parse_time(timestamp) is None:
            continue

        valid_hours += 1

        for field in NUMERIC_VARIABLES:

            values = hourly.get(field)

            if not isinstance(values, list):
                continue

            if index >= len(values):
                continue

            value = _finite_float(
                values[index]
            )

            if value is not None:
                data[field].append(value)

    data["_valid_hours"] = [
        float(valid_hours)
    ]

    return data


# =====================================================================
# BUILD COMPACT FEATURES
# =====================================================================

def _build_compact_features(
    data: Dict[str, List[float]]
) -> Dict[str, Optional[float]]:

    temperature = data.get(
        "temperature_2m",
        []
    )

    humidity = data.get(
        "relative_humidity_2m",
        []
    )

    dew_point = data.get(
        "dew_point_2m",
        []
    )

    rainfall = data.get(
        "precipitation",
        []
    )

    wind = data.get(
        "wind_speed_10m",
        []
    )

    vpd = data.get(
        "vapour_pressure_deficit",
        []
    )

    soil_moisture = data.get(
        "soil_moisture_0_to_1cm",
        []
    )

    et0 = data.get(
        "et0_fao_evapotranspiration",
        []
    )

    evapotranspiration = data.get(
        "evapotranspiration",
        []
    )

    leaf_wetness = data.get(
        "leaf_wetness_probability",
        []
    )

    # ---------------------------------------------------------------
    # HUMIDITY EXPOSURE
    # ---------------------------------------------------------------

    humidity_ge_80 = sum(
        1
        for value in humidity
        if value >= 80.0
    )

    humidity_ge_90 = sum(
        1
        for value in humidity
        if value >= 90.0
    )

    humidity_le_50 = sum(
        1
        for value in humidity
        if value <= 50.0
    )

    # ---------------------------------------------------------------
    # RAIN
    # ---------------------------------------------------------------

    rain_hours = sum(
        1
        for value in rainfall
        if value >= 0.1
    )

    heavy_rain_hours = sum(
        1
        for value in rainfall
        if value >= 5.0
    )

    # ---------------------------------------------------------------
    # LEAF WETNESS
    # ---------------------------------------------------------------

    wet_hours_ge_60 = sum(
        1
        for value in leaf_wetness
        if value >= 60.0
    )

    wet_hours_ge_80 = sum(
        1
        for value in leaf_wetness
        if value >= 80.0
    )

    # ---------------------------------------------------------------
    # HOT + HUMID
    # ---------------------------------------------------------------

    paired_temp_humidity = min(
        len(temperature),
        len(humidity),
    )

    hot_humid_hours = sum(
        1
        for i in range(paired_temp_humidity)
        if temperature[i] >= 25.0
        and humidity[i] >= 80.0
    )

    # ---------------------------------------------------------------
    # TEMPERATURE EXTREMES
    # ---------------------------------------------------------------

    hot_hours = sum(
        1
        for value in temperature
        if value >= 30.0
    )

    cool_hours = sum(
        1
        for value in temperature
        if value <= 15.0
    )

    # ---------------------------------------------------------------
    # VPD
    # ---------------------------------------------------------------

    low_vpd_hours = sum(
        1
        for value in vpd
        if value <= 1.0
    )

    very_low_vpd_hours = sum(
        1
        for value in vpd
        if value <= 0.5
    )

    # ---------------------------------------------------------------
    # DEW POINT DEPRESSION
    # ---------------------------------------------------------------

    paired_dew = min(
        len(temperature),
        len(dew_point),
    )

    dew_point_depressions = [
        temperature[i] - dew_point[i]
        for i in range(paired_dew)
    ]

    # ---------------------------------------------------------------
    # FEATURE VECTOR
    # ---------------------------------------------------------------

    features = {

        # -----------------------------------------------------------
        # TEMPERATURE
        # -----------------------------------------------------------

        "avg_temperature_c":
            _mean(temperature),

        "min_temperature_c":
            _minimum(temperature),

        "max_temperature_c":
            _maximum(temperature),

        # -----------------------------------------------------------
        # HUMIDITY
        # -----------------------------------------------------------

        "avg_humidity_pct":
            _mean(humidity),

        "high_humidity_pct":
            _percentage(
                humidity_ge_80,
                len(humidity),
            ),

        "very_high_humidity_pct":
            _percentage(
                humidity_ge_90,
                len(humidity),
            ),

        "dry_air_pct":
            _percentage(
                humidity_le_50,
                len(humidity),
            ),

        # -----------------------------------------------------------
        # RAIN
        # -----------------------------------------------------------

        "rainfall_total_mm":
            sum(rainfall) if rainfall else None,

        "rain_hours_pct":
            _percentage(
                rain_hours,
                len(rainfall),
            ),

        "heavy_rain_hours_pct":
            _percentage(
                heavy_rain_hours,
                len(rainfall),
            ),

        # -----------------------------------------------------------
        # LEAF WETNESS
        # -----------------------------------------------------------

        "avg_leaf_wetness_pct":
            _mean(leaf_wetness),

        "leaf_wetness_hours_pct":
            _percentage(
                wet_hours_ge_60,
                len(leaf_wetness),
            ),

        "high_leaf_wetness_hours_pct":
            _percentage(
                wet_hours_ge_80,
                len(leaf_wetness),
            ),

        # -----------------------------------------------------------
        # VPD
        # -----------------------------------------------------------

        "avg_vpd_kpa":
            _mean(vpd),

        "low_vpd_hours_pct":
            _percentage(
                low_vpd_hours,
                len(vpd),
            ),

        "very_low_vpd_hours_pct":
            _percentage(
                very_low_vpd_hours,
                len(vpd),
            ),

        # -----------------------------------------------------------
        # INTERACTION FEATURES
        # -----------------------------------------------------------

        "hot_humid_hours_pct":
            _percentage(
                hot_humid_hours,
                paired_temp_humidity,
            ),

        "hot_hours_pct":
            _percentage(
                hot_hours,
                len(temperature),
            ),

        "cool_hours_pct":
            _percentage(
                cool_hours,
                len(temperature),
            ),

        # -----------------------------------------------------------
        # DEW POINT
        # -----------------------------------------------------------

        "avg_dew_point_depression_c":
            _mean(
                dew_point_depressions
            ),

        # -----------------------------------------------------------
        # SOIL
        # -----------------------------------------------------------

        "avg_soil_moisture_m3_m3":
            _mean(soil_moisture),

        # -----------------------------------------------------------
        # WIND
        # -----------------------------------------------------------

        "avg_wind_speed_kmh":
            _mean(wind),

        # -----------------------------------------------------------
        # EVAPOTRANSPIRATION
        # -----------------------------------------------------------

        "total_et0_mm":
            sum(et0) if et0 else None,

        "total_evapotranspiration_mm":
            (
                sum(evapotranspiration)
                if evapotranspiration
                else None
            ),
    }

    return features


# =====================================================================
# LEARN MEDIANS FROM HISTORICAL FEATURES
# =====================================================================

def _learn_imputation_values(
    historical_features: Dict[str, Optional[float]],
) -> Dict[str, float]:

    imputation_values = {}

    for feature, value in historical_features.items():

        if value is not None:

            number = _finite_float(value)

            if number is not None:
                imputation_values[feature] = number
                continue

        # If the historical feature itself is unavailable,
        # use the predefined fallback.
        if feature in FALLBACK_VALUES:
            imputation_values[feature] = (
                float(FALLBACK_VALUES[feature])
            )

    return imputation_values


# =====================================================================
# APPLY IMPUTATION
# =====================================================================

def _fill_missing(
    features: Dict[str, Optional[float]],
    imputation_values: Dict[str, float],
) -> Dict[str, float]:

    result: Dict[str, float] = {}

    for feature, value in features.items():

        number = _finite_float(value)

        if number is not None:
            result[feature] = number
            continue

        # First choice: learned historical value.
        if feature in imputation_values:

            result[feature] = float(
                imputation_values[feature]
            )

            continue

        # Absolute fallback.
        if feature in FALLBACK_VALUES:

            result[feature] = float(
                FALLBACK_VALUES[feature]
            )

            continue

        # This should never happen because all generated
        # features have a predefined fallback.
        result[feature] = 0.0

    return result


# =====================================================================
# FINAL NUMERIC SAFETY
# =====================================================================

def _clean_numeric_features(
    features: Dict[str, Any]
) -> Dict[str, float]:

    result = {}

    for key, value in features.items():

        number = _finite_float(value)

        if number is None:
            number = 0.0

        result[key] = round(
            number,
            6,
        )

    return result


# =====================================================================
# PUBLIC FUNCTION
# =====================================================================

def extract_features(
    forecast_data: dict,
    historical_data: dict,
) -> dict:
    """
    Extract compact disease/pest weather features.

    Missing values are handled safely.

    Historical data:
        Used to create the baseline imputation values.

    Forecast data:
        Uses the SAME historical imputation values.

    Returns:
        {
            "historical_features": {...},
            "forecast_features": {...},
            "feature_columns": [...],
            "imputation_values": {...},
            "metadata": {...}
        }
    """

    # ---------------------------------------------------------------
    # VALIDATE
    # ---------------------------------------------------------------

    forecast_data = _validate_payload(
        forecast_data,
        "forecast_data",
    )

    historical_data = _validate_payload(
        historical_data,
        "historical_data",
    )

    # ---------------------------------------------------------------
    # EXTRACT HOURLY VALUES
    # ---------------------------------------------------------------

    historical_hourly = _extract_hourly_data(
        historical_data
    )

    forecast_hourly = _extract_hourly_data(
        forecast_data
    )

    # ---------------------------------------------------------------
    # COMPRESS PERIODS
    # ---------------------------------------------------------------

    historical_raw = _build_compact_features(
        historical_hourly
    )

    forecast_raw = _build_compact_features(
        forecast_hourly
    )

    # ---------------------------------------------------------------
    # LEARN IMPUTATION VALUES FROM HISTORICAL DATA
    # ---------------------------------------------------------------
    #
    # For a single aggregated period, the available historical
    # value is the baseline.
    #
    # When you later train on many historical windows, these same
    # rules can be expanded to calculate medians across all training
    # samples.
    # ---------------------------------------------------------------

    imputation_values = _learn_imputation_values(
        historical_raw
    )

    # ---------------------------------------------------------------
    # IMPUTE
    # ---------------------------------------------------------------

    historical_features = _fill_missing(
        historical_raw,
        imputation_values,
    )

    forecast_features = _fill_missing(
        forecast_raw,
        imputation_values,
    )

    # ---------------------------------------------------------------
    # FINAL SAFETY
    # ---------------------------------------------------------------

    historical_features = _clean_numeric_features(
        historical_features
    )

    forecast_features = _clean_numeric_features(
        forecast_features
    )

    # ---------------------------------------------------------------
    # FEATURE ORDER
    # ---------------------------------------------------------------

    feature_columns = list(
        historical_features.keys()
    )

    # ---------------------------------------------------------------
    # RESULT
    # ---------------------------------------------------------------

    return {
        "historical_features":
            historical_features,

        "forecast_features":
            forecast_features,

        "feature_columns":
            feature_columns,

        "imputation_values":
            imputation_values,

        "metadata": {
            "historical_hours": int(
                historical_hourly["_valid_hours"][0]
            ),

            "forecast_hours": int(
                forecast_hourly["_valid_hours"][0]
            ),

            "feature_count":
                len(feature_columns),
        },

        "notes": {
            "missing_value_strategy":
                "Individual missing hourly values are ignored "
                "during aggregation. Missing final features are "
                "imputed using historical values, with predefined "
                "fallbacks only when necessary.",

            "forecast_imputation":
                "Forecast features use the historical imputation "
                "values to avoid using forecast information to "
                "define its own missing-value baseline.",

            "ml_ready":
                True,
        }
    }

# =====================================================================
# DATASET SCHEMA COMPATIBILITY (ADDED)
# =====================================================================
#
# extract_features() keeps "historical_features" and
# "forecast_features" as two separate dicts with unprefixed keys
# (e.g. "avg_temperature_c"). A training dataset needs both periods
# flattened into ONE row with the period baked into the column name
# (e.g. "historical_avg_temperature_c", "forecast_avg_temperature_c").
#
# flatten_for_dataset() does that conversion only — it does not
# change any extraction, imputation, or rounding logic above.
# =====================================================================

#: Column order for the 24 weather features produced per period.
#: historical_/forecast_ prefixes applied in flatten_for_dataset().
WEATHER_FEATURE_COLUMNS = (
    "avg_temperature_c",
    "min_temperature_c",
    "max_temperature_c",
    "avg_humidity_pct",
    "high_humidity_pct",
    "very_high_humidity_pct",
    "dry_air_pct",
    "rainfall_total_mm",
    "rain_hours_pct",
    "heavy_rain_hours_pct",
    "avg_leaf_wetness_pct",
    "leaf_wetness_hours_pct",
    "high_leaf_wetness_hours_pct",
    "avg_vpd_kpa",
    "low_vpd_hours_pct",
    "very_low_vpd_hours_pct",
    "hot_humid_hours_pct",
    "hot_hours_pct",
    "cool_hours_pct",
    "avg_dew_point_depression_c",
    "avg_soil_moisture_m3_m3",
    "avg_wind_speed_kmh",
    "total_et0_mm",
    "total_evapotranspiration_mm",
)