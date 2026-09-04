from disease_detect import disease_detection
from pest_detection import pest_detection
from pest_information import get_pest_info
from flatten import flatten_weather_features, temp_humid, other
from soil import predict_soil_characteristics
from fertilizer_predict import predict_fertilizer
from risk_score import predict_risk_score

kb = {}

def diseasefunc(file_path, model_path):
    diseasedata = disease_detection(file_path=file_path, model_path=model_path)
    dis_name = diseasedata[0]['disease_name']
    dis_conf = diseasedata[0]['confidence']
    dis_annotation_path = diseasedata[0]['saved_path']
    return {'disease_name': dis_name,
            'confidence': dis_conf,
            'annotation_path': dis_annotation_path
    }

def call_models(
        disease_or_pest: str,
        address: str,
        soil_type: str,
        filepath: str,
        disease_category: str = None
):
    disease_or_pest = disease_or_pest.lower()
    disease_category = disease_category.lower() if disease_category is not None else None

    if "disease" in disease_or_pest:
        if "wheat" in disease_category:
            diseasedata = diseasefunc(file_path=filepath, model_path="best0.pt")
            dname = diseasedata['disease_name']
            dconf = diseasedata['confidence']
            dannpath = diseasedata['annotation_path']
        elif "rice" in disease_category:
            diseasedata = diseasefunc(file_path=filepath, model_path="best.pt")
            dname = diseasedata['disease_name']
            dconf = diseasedata['confidence']
            dannpath = diseasedata['annotation_path']
        elif "other" in disease_category:
            diseasedata = diseasefunc(file_path=filepath, model_path="PlantDiseaseDetection.pt")
            dname = diseasedata['disease_name']
            dconf = diseasedata['confidence']
            dannpath = diseasedata['annotation_path']
        else:
            print("fku")

    elif "pest" in disease_or_pest:
        pestdata = pest_detection(file_path=filepath, model_path="best1.pt")
        pest_info = dict(get_pest_info(pestdata[0]['pest_name']))
        confidence = pestdata[0]['confidence']
        annotationpath = pestdata[0]['saved_path']
    else:
        print("fku")

    temp, humid = temp_humid(address)
    soildata = predict_soil_characteristics(address)
    N = soildata['N_level']
    P = soildata['P_level']
    K = soildata['K_level']
    PH = soildata['pH_level']
    fertilizerdata = predict_fertilizer(soil_type=soil_type,
                                        ph_level=PH,
                                        humidity=humid,
                                        temperature=temp,
                                        nitrogen_level=N,
                                        potassium_level=K,
                                        phosphorus_level=P)
    riskscore = round(float(predict_risk_score(flatten_weather_features(address, isstp=disease_or_pest, stp=soil_type))), 2)
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

    return kb