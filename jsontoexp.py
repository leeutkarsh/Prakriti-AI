import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(r"D:\Prakriti AI\.env"), override=True)

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

def explain_detection(json_data, disease_or_pest):
    if not isinstance(disease_or_pest, str):
        raise ValueError("disease_or_pest must be either 'disease' or 'pest'.")

    disease_or_pest = disease_or_pest.lower().strip()

    if disease_or_pest not in {"disease", "pest"}:
        raise ValueError("disease_or_pest must be either 'disease' or 'pest'.")

    if isinstance(json_data, dict):
        data = json_data
    elif isinstance(json_data, str):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON data.") from e
    else:
        raise TypeError("json_data must be a dictionary or JSON string.")

    if not isinstance(data, dict):
        raise ValueError("JSON data must contain an object.")

    if disease_or_pest == "disease":
        relevant_data = {
            "Disease/Pest Type": data.get("Disease/Pest Type"),
            "Disease/Pest Category": data.get("Disease/Pest Category"),
            "Disease Name": data.get("Disease Name"),
            "Disease Confidence": data.get("Disease Confidence"),
            "Address": data.get("Address"),
            "Soil Type": data.get("Soil Type"),
            "Temperature": data.get("Temperature"),
            "Humidity": data.get("Humidity"),
            "Soil Nitrogen Level": data.get("Soil Nitrogen Level"),
            "Soil Phosphorus Level": data.get("Soil Phosphorus Level"),
            "Soil Potassium Level": data.get("Soil Potassium Level"),
            "Soil pH Level": data.get("Soil pH Level"),
            "Fertilizer Recommendation": data.get("Fertilizer Recommendation"),
            "Risk Score": data.get("Risk Score"),
            "Soil Temperature": data.get("Soil Temperature"),
            "Soil Moisture": data.get("Soil Moisture"),
            "Rainfall": data.get("Rainfall")
        }
    else:
        relevant_data = {
            "Disease/Pest Type": data.get("Disease/Pest Type"),
            "Disease/Pest Category": data.get("Disease/Pest Category"),
            "Pest Name": data.get("Pest Name"),
            "Pest Confidence": data.get("Pest Confidence"),
            "Pest Information": data.get("Pest Information"),
            "Address": data.get("Address"),
            "Soil Type": data.get("Soil Type"),
            "Temperature": data.get("Temperature"),
            "Humidity": data.get("Humidity"),
            "Soil Nitrogen Level": data.get("Soil Nitrogen Level"),
            "Soil Phosphorus Level": data.get("Soil Phosphorus Level"),
            "Soil Potassium Level": data.get("Soil Potassium Level"),
            "Soil pH Level": data.get("Soil pH Level"),
            "Fertilizer Recommendation": data.get("Fertilizer Recommendation"),
            "Risk Score": data.get("Risk Score"),
            "Soil Temperature": data.get("Soil Temperature"),
            "Soil Moisture": data.get("Soil Moisture"),
            "Rainfall": data.get("Rainfall")
        }

    relevant_data = {
        key: value
        for key, value in relevant_data.items()
        if value is not None
    }

    prompt = f"""
You are an agricultural AI assistant.

Analyze the following plant {disease_or_pest} detection and environmental data.

Your task is to explain the result to a farmer or agriculture professional in clear, practical language.

Detection type:
{disease_or_pest}

Data:
{json.dumps(relevant_data, indent=2, ensure_ascii=False)}

Provide a concise but useful explanation covering:

1. What was detected and how confident the model is.
2. What the detected disease or pest means.
3. How the current temperature, humidity, rainfall, soil temperature, and soil moisture may affect the situation.
4. What the soil N, P, K and pH levels indicate.
5. What the fertilizer recommendation means.
6. What the risk score indicates.
7. Practical precautions or management steps relevant to the detected disease or pest.

Do not invent facts that are not supported by the provided data.
Clearly distinguish model predictions from general agricultural guidance.
Do not mention that you are an AI.
Do not discuss internal model reasoning.
Use headings where helpful.
"""

    completion = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.6,
        max_tokens=16384,
        reasoning_effort="medium",
        stream=True
    )

    result = []

    for chunk in completion:
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            result.append(content)

    return "".join(result).strip()