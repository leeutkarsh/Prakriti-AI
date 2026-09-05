Absolutely — here’s a clean Markdown task specification you can give directly to your teammate.

JSON Disease & Pest Explanation Function

1. Objective

Create a Python function that accepts:

1. A JSON-format text/string containing information about both diseases and pests.
2. A parameter specifying what the user wants to analyze:
   - ""disease""
   - ""pest""

The function should then extract and explain only the information relevant to the selected category.

The JSON may contain information about both diseases and pests, but the user will select which type they want to detect/analyze.

---

2. Expected Function

Create a function similar to:

def explain_detection(json_text, detection_type):
    ...

Parameters

"json_text"

A JSON-format string containing the complete detection/forecast information.

Example:

json_text = '''
{
    "disease": {
        "name": "Rice Blast",
        "confidence": 0.94,
        "severity": "High",
        "symptoms": ["Brown lesions", "Leaf damage"],
        "weather_conditions": {
            "temperature": 28,
            "humidity": 85
        },
        "risk": 0.82
    },
    "pest": {
        "name": "Rice Stem Borer",
        "confidence": 0.89,
        "severity": "Medium",
        "symptoms": ["Dead hearts", "White ears"],
        "risk": 0.64
    }
}
'''

"detection_type"

Determines which section of the JSON should be explained.

Allowed values:

"disease"
"pest"

Example:

explain_detection(json_text, "disease")

or:

explain_detection(json_text, "pest")

---

3. Core Requirement

The function must not explain irrelevant information.

If:

detection_type = "disease"

Then explain:

- Disease name
- Disease confidence
- Disease severity
- Disease symptoms
- Disease risk
- Disease-related weather conditions
- Disease-related forecast information
- Disease-related recommendations
- Any other disease-specific information present in the JSON

Ignore pest-related information.

---

If:

detection_type = "pest"

Then explain:

- Pest name
- Pest confidence
- Pest severity
- Pest symptoms
- Pest risk
- Pest-related weather conditions
- Pest-related forecast information
- Pest-related recommendations
- Any other pest-specific information present in the JSON

Ignore disease-related information.

---

4. Important Requirement — Dynamic JSON

Do not hard-code only the example fields.

The JSON structure may contain additional information in the future.

For example, the JSON could contain:

{
    "disease": {
        "name": "Rice Blast",
        "confidence": 0.94,
        "severity": "High",
        "cause": "Fungal infection",
        "symptoms": [],
        "spread_rate": "Fast",
        "weather_conditions": {},
        "forecast": {},
        "recommendations": [],
        "treatment": {},
        "additional_information": {}
    }
}

The function should be able to process these fields without needing to manually modify the function every time a new field is added.

The explanation should therefore be generated dynamically from the JSON data.

---

5. Explanation Requirements

The output should be understandable to a normal user/farmer.

Do not simply return the raw JSON.

For example, instead of:

confidence: 0.94
severity: High
risk: 0.82

The output should explain:

The detected disease is Rice Blast with a confidence of 94%.
The current severity is classified as High, which indicates that the disease may
cause significant damage if it continues to spread.

The estimated risk level is 82%, indicating a relatively high possibility of
disease development or spread under the current conditions.

The exact wording can be generated dynamically.

---

6. Output Should Explain Every Relevant Field

If the selected category contains:

{
    "name": "Rice Blast",
    "confidence": 0.94,
    "severity": "High",
    "temperature": 28,
    "humidity": 85
}

The function should explain all of them.

For example:

Disease: Rice Blast

Detection Confidence:
The model is 94% confident that the detected disease is Rice Blast.

Severity:
The disease severity is classified as High, indicating that the disease
may currently pose a significant threat to the crop.

Temperature:
The recorded temperature is 28°C.

Humidity:
The humidity is 85%, which may create conditions favorable for disease
development depending on the disease.

---

7. Handling Nested JSON

The function must also support nested objects.

Example:

{
    "disease": {
        "name": "Rice Blast",
        "risk": {
            "current": 0.82,
            "next_7_days": 0.91
        },
        "weather": {
            "temperature": 28,
            "humidity": 85,
            "rainfall": 12
        }
    }
}

The function should recursively process the nested information.

Example explanation:

Disease: Rice Blast

Current Risk:
The current estimated risk is 82%.

7-Day Risk:
The estimated risk for the next 7 days is 91%.

Weather Conditions:
Temperature: 28°C
Humidity: 85%
Rainfall: 12 mm

---

8. Handling Arrays / Lists

The function must also handle lists.

Example:

{
    "disease": {
        "symptoms": [
            "Brown spots on leaves",
            "Leaf lesions",
            "Premature drying"
        ]
    }
}

The output should explain them naturally:

Observed Symptoms:

1. Brown spots on leaves
2. Leaf lesions
3. Premature drying

The same should work for lists of recommendations, treatments, affected crops, weather conditions, etc.

---

9. Missing / None Values

The JSON may contain values such as:

{
    "disease": {
        "name": "Rice Blast",
        "confidence": null,
        "severity": null,
        "forecast": null
    }
}

The function should not crash.

It should either:

- Skip unavailable fields, or
- Clearly state that the information is unavailable.

Example:

Detection Confidence:
Confidence information is currently unavailable.

Forecast:
No forecast information is currently available.

Do not produce errors such as:

NoneType object...

---

10. Invalid Detection Type

If the user provides:

explain_detection(json_text, "something")

The function should return a clear error.

Example:

Invalid detection type. Please select either 'disease' or 'pest'.

---

11. Invalid JSON

If the provided text is not valid JSON, the function should handle the error gracefully.

Example:

Unable to process the provided data because the input is not valid JSON.

The application should not crash.

---

12. Suggested Processing Flow

The function should roughly follow this architecture:

JSON text
   ↓
Parse JSON
   ↓
Validate detection_type
   ↓
Select disease OR pest section
   ↓
Extract selected category
   ↓
Recursively process nested data
   ↓
Explain each relevant field
   ↓
Return human-readable explanation

---

13. Important Separation of Responsibilities

The function should focus on:

«Taking structured JSON data and converting it into an understandable explanation.»

It should not perform disease or pest detection itself.

Detection will already have happened elsewhere.

For example:

YOLO / ML Model
      ↓
Detection Result
      ↓
Forecast / Risk Processing
      ↓
JSON
      ↓
explain_detection()
      ↓
Human-readable explanation
      ↓
Frontend / Farmer

---

14. AI API Integration

The function should ideally be designed so that its output can later be passed to an LLM/AI API.

For example:

JSON
 ↓
Filter disease/pest information
 ↓
Prepare structured information
 ↓
Send relevant information to AI
 ↓
AI generates simple explanation
 ↓
Return explanation to frontend

The AI should only receive the selected category's information.

For example, if the user selects:

disease

Do not unnecessarily send the complete pest data to the AI.

This reduces irrelevant information and makes the explanation more focused.

---

15. Example Usage

Disease

result = explain_detection(json_text, "disease")

print(result)

Expected concept:

Disease Analysis

Rice Blast was detected with 94% confidence.

Severity:
High

Risk:
82%

Symptoms:
- Brown lesions
- Leaf damage

Weather:
- Temperature: 28°C
- Humidity: 85%

Overall:
The current conditions indicate a relatively high risk of Rice Blast
development and spread.

---

Pest

result = explain_detection(json_text, "pest")

print(result)

Expected concept:

Pest Analysis

Rice Stem Borer was detected with 89% confidence.

Severity:
Medium

Risk:
64%

Symptoms:
- Dead hearts
- White ears

Overall:
The detected pest presents a moderate risk to the crop.

---

16. Final Requirements Checklist

The implementation must:

- [ ] Accept JSON-format text/string.
- [ ] Accept ""disease"" or ""pest"" as a second parameter.
- [ ] Select only the requested category.
- [ ] Ignore irrelevant disease/pest information.
- [ ] Explain every relevant field.
- [ ] Support nested JSON objects.
- [ ] Support lists/arrays.
- [ ] Handle "null" / "None" values.
- [ ] Handle invalid JSON safely.
- [ ] Handle invalid "detection_type".
- [ ] Work with additional fields without requiring constant code changes.
- [ ] Return a human-readable explanation.
- [ ] Keep the function independent from the actual ML detection model.
- [ ] Structure the implementation so an LLM API can optionally be integrated later.

Main Goal

Build a generic JSON-to-explanation function that can take the output generated by our disease/pest detection and forecasting pipeline and convert it into a clear explanation based on what the user selected:

"disease" → Disease information only

"pest" → Pest information only

The function should be dynamic rather than hard-coded, because the JSON structure may evolve as more information is added to the project.