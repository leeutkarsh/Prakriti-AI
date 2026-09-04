import joblib
import pandas as pd
import xgboost as xgb

try:
    loaded_ordinal_encoder = joblib.load('ordinal_encoder_preprocessor.joblib')
    print("OrdinalEncoder preprocessor loaded successfully.")
except FileNotFoundError:
    print("Error: 'ordinal_encoder_preprocessor.joblib' not found. Please ensure the file exists.")
    loaded_ordinal_encoder = None

try:
    loaded_xgb_model = xgb.XGBRegressor()
    loaded_xgb_model.load_model('xgboost_regressor_model.json')
    print("XGBoost model loaded successfully.")
except Exception as e:
    print(f"Error loading XGBoost model: {e}. Please ensure the file exists.")
    loaded_xgb_model = None

categorical_cols_for_prediction = ['Soil_Type', 'N_level', 'P_level', 'K_level', 'Ph_level', 'Issue_type']

feature_columns_order = ['historical_avg_temperature_c',
 'historical_min_temperature_c',
 'historical_max_temperature_c',
 'historical_avg_humidity_pct',
 'historical_high_humidity_pct',
 'historical_very_high_humidity_pct',
 'historical_dry_air_pct',
 'historical_rainfall_total_mm',
 'historical_rain_hours_pct',
 'historical_heavy_rain_hours_pct',
 'historical_avg_leaf_wetness_pct',
 'historical_leaf_wetness_hours_pct',
 'historical_high_leaf_wetness_hours_pct',
 'historical_avg_vpd_kpa',
 'historical_low_vpd_hours_pct',
 'historical_very_low_vpd_hours_pct',
 'historical_hot_humid_hours_pct',
 'historical_hot_hours_pct',
 'historical_cool_hours_pct',
 'historical_avg_dew_point_depression_c',
 'historical_avg_soil_moisture_m3_m3',
 'historical_avg_wind_speed_kmh',
 'historical_total_et0_mm',
 'historical_total_evapotranspiration_mm',
 'forecast_avg_temperature_c',
 'forecast_min_temperature_c',
 'forecast_max_temperature_c',
 'forecast_avg_humidity_pct',
 'forecast_high_humidity_pct',
 'forecast_very_high_humidity_pct',
 'forecast_dry_air_pct',
 'forecast_rainfall_total_mm',
 'forecast_rain_hours_pct',
 'forecast_heavy_rain_hours_pct',
 'forecast_avg_leaf_wetness_pct',
 'forecast_leaf_wetness_hours_pct',
 'forecast_high_leaf_wetness_hours_pct',
 'forecast_avg_vpd_kpa',
 'forecast_low_vpd_hours_pct',
 'forecast_very_low_vpd_hours_pct',
 'forecast_hot_humid_hours_pct',
 'forecast_hot_hours_pct',
 'forecast_cool_hours_pct',
 'forecast_avg_dew_point_depression_c',
 'forecast_avg_soil_moisture_m3_m3',
 'forecast_avg_wind_speed_kmh',
 'forecast_total_et0_mm',
 'forecast_total_evapotranspiration_mm',
 'Soil_Type',
 'N_level',
 'P_level',
 'K_level',
 'Ph_level',
 'Issue_type']

def predict_risk_score(input_parameters: dict) -> float:
    """
    Predicts the risk score based on input parameters.

    Args:
        input_parameters (dict): A dictionary where keys are feature names
                                 and values are their respective values.
                                 Must contain all 54 features used during training.

    Returns:
        float: The predicted risk score.
        Raises ValueError if the model or preprocessor could not be loaded.
    """
    if loaded_xgb_model is None or loaded_ordinal_encoder is None:
        raise ValueError("Model or preprocessor not loaded. Cannot make predictions.")

    input_df = pd.DataFrame([input_parameters], columns=feature_columns_order)

    input_df[categorical_cols_for_prediction] = loaded_ordinal_encoder.transform(input_df[categorical_cols_for_prediction])

    predicted_score = loaded_xgb_model.predict(input_df)

    return predicted_score[0]