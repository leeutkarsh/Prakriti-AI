from disease_detect import disease_detection
from jsontoexp import explain_detection
from pest_detection import pest_detection
from pest_information import get_pest_info
from flatten import flatten_weather_features, temp_humid, other
from soil import predict_soil_characteristics
from fertilizer_predict import predict_fertilizer
from risk_score import predict_risk_score
from status import update_status

kb = {}


def diseasefunc(file_path, model_path):
    diseasedata = disease_detection(
        file_path=file_path,
        model_path=model_path
    )

    if (
        not isinstance(diseasedata, list)
        or len(diseasedata) == 0
        or not isinstance(diseasedata[0], dict)
        or not diseasedata[0].get("disease_name")
        or diseasedata[0].get("confidence") is None
        or not diseasedata[0].get("saved_path")
    ):
        diseasedata = disease_detection(
            file_path=file_path,
            model_path="PlantDiseaseDetection.pt"
        )

    if (
        not isinstance(diseasedata, list)
        or len(diseasedata) == 0
        or not isinstance(diseasedata[0], dict)
        or not diseasedata[0].get("disease_name")
        or diseasedata[0].get("confidence") is None
        or not diseasedata[0].get("saved_path")
    ):
        raise RuntimeError("Disease detection failed on both models.")

    return {
        "disease_name": diseasedata[0]["disease_name"],
        "confidence": diseasedata[0]["confidence"],
        "annotation_path": diseasedata[0]["saved_path"]
    }

def call_models(
        disease_or_pest: str,
        address: str,
        soil_type: str,
        filepath: str,
        disease_category: str = None
):
    disease_or_pest = disease_or_pest.lower()
    disease_category = disease_category.lower() if disease_category else None

    dname = None
    dconf = None
    dannpath = None

    pestdata = []
    pest_info = None
    confidence = None
    annotationpath = None

    if "disease" in disease_or_pest:
        update_status("processing", "disease_detection", "Detecting disease...")

        if disease_category and "wheat" in disease_category:
            update_status(
                "processing",
                "disease_detection",
                "Running wheat disease detection..."
            )

            diseasedata = diseasefunc(
                file_path=filepath,
                model_path="best0.pt"
            )

        elif disease_category and "rice" in disease_category:
            update_status(
                "processing",
                "disease_detection",
                "Running rice disease detection..."
            )

            diseasedata = diseasefunc(
                file_path=filepath,
                model_path="best.pt"
            )

        elif disease_category and "other" in disease_category:
            update_status(
                "processing",
                "disease_detection",
                "Running disease detection..."
            )

            diseasedata = diseasefunc(
                file_path=filepath,
                model_path="PlantDiseaseDetection.pt"
            )

        else:
            raise ValueError("Unknown disease category.")

        dname = diseasedata["disease_name"]
        dconf = diseasedata["confidence"]
        dannpath = diseasedata["annotation_path"]

    elif "pest" in disease_or_pest:
        update_status("processing", "pest_detection", "Detecting pest...")

        pestdata = pest_detection(
            file_path=filepath,
            model_path="best1.pt"
        )

        if not pestdata:
            raise RuntimeError("Pest detection failed.")

        update_status(
            "processing",
            "pest_information",
            "Fetching pest information..."
        )

        pest_info = dict(
            get_pest_info(pestdata[0]["pest_name"])
        )

        confidence = pestdata[0]["confidence"]
        annotationpath = pestdata[0]["saved_path"]

    else:
        raise ValueError(
            "disease_or_pest must contain either 'disease' or 'pest'."
        )

    update_status(
        "processing",
        "weather_analysis",
        "Analyzing weather conditions..."
    )

    temp, humid = temp_humid(address)

    update_status(
        "processing",
        "soil_analysis",
        "Analyzing soil characteristics..."
    )

    soildata = predict_soil_characteristics(address)

    N = soildata["N_level"]
    P = soildata["P_level"]
    K = soildata["K_level"]
    PH = soildata["pH_level"]

    update_status(
        "processing",
        "fertilizer_prediction",
        "Generating fertilizer recommendation..."
    )

    fertilizerdata = predict_fertilizer(
        soil_type=soil_type,
        ph_level=PH,
        humidity=humid,
        temperature=temp,
        nitrogen_level=N,
        potassium_level=K,
        phosphorus_level=P
    )

    update_status(
        "processing",
        "risk_analysis",
        "Calculating risk score..."
    )

    riskscore = round(
        float(
            predict_risk_score(
                flatten_weather_features(
                    address,
                    isstp=disease_or_pest,
                    stp=soil_type
                )
            )
        ),
        2
    )

    update_status(
        "processing",
        "environment_analysis",
        "Analyzing soil and environmental conditions..."
    )

    soiltemp, soilmois, rainfall, unitdata = other(address)

    kb = {
        "Disease/Pest Type": disease_or_pest,
        "Disease/Pest Category": disease_category,
        "Address": address,
        "Soil Type": soil_type,

        "Disease Name": dname if "disease" in disease_or_pest else None,
        "Disease Confidence": dconf if "disease" in disease_or_pest else None,
        "Disease Annotation Path": dannpath if "disease" in disease_or_pest else None,

        "Pest Name": pestdata[0]["pest_name"] if "pest" in disease_or_pest else None,
        "Pest Confidence": confidence if "pest" in disease_or_pest else None,
        "Pest Annotation Path": annotationpath if "pest" in disease_or_pest else None,
        "Pest Information": pest_info if "pest" in disease_or_pest else None,

        "Temperature": temp,
        "Humidity": humid,

        "Soil Nitrogen Level": N,
        "Soil Phosphorus Level": P,
        "Soil Potassium Level": K,
        "Soil pH Level": PH,

        "Fertilizer Recommendation": fertilizerdata,

        "Risk Score": riskscore,

        "Soil Temperature": soiltemp,
        "Soil Moisture": soilmois,
        "Rainfall": rainfall,
        "Units": unitdata
    }

    update_status(
        "processing",
        "detection explanation",
        "Generating simple explanations..."
    )

    kb["Explanation"] = str(explain_detection(kb, "disease"))

    update_status(
        "completed",
        "finished",
        "Analysis completed successfully"
    )

    return kb
