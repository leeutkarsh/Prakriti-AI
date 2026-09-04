import joblib
import pandas as pd

MODEL_PATH = "fertilizer_model.pkl"

data = joblib.load(MODEL_PATH)

model = data["model"]
soil_encoder = data["soil_encoder"]
level_encoder = data["level_encoder"]
target_encoder = data["target_encoder"]
features = data["features"]

def predict_fertilizer(
    soil_type,
    ph_level,
    nitrogen_level,
    phosphorus_level,
    potassium_level,
    temperature,
    humidity
):

    input_data = pd.DataFrame([{
        "Soil_Type": soil_type,
        "pH_Level": ph_level,
        "Nitrogen_Level": nitrogen_level,
        "Phosphorus_Level": phosphorus_level,
        "Potassium_Level": potassium_level,
        "Temperature_C": temperature,
        "Humidity_Pct": humidity
    }])

    soil_encoded = soil_encoder.transform(
        input_data[["Soil_Type"]]
    )

    soil_columns = soil_encoder.get_feature_names_out(
        ["Soil_Type"]
    )

    soil_df = pd.DataFrame(
        soil_encoded,
        columns=soil_columns
    )

    level_columns = [
        "pH_Level",
        "Nitrogen_Level",
        "Phosphorus_Level",
        "Potassium_Level"
    ]

    input_data[level_columns] = level_encoder.transform(
        input_data[level_columns]
    )

    input_data = pd.concat(
        [
            input_data.drop(columns=["Soil_Type"]),
            soil_df
        ],
        axis=1
    )

    input_data = input_data[features]

    prediction = model.predict(input_data)[0]

    fertilizer = target_encoder.inverse_transform(
        [prediction]
    )[0]

    return {
        "fertilizer": fertilizer
    }