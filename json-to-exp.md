# JSON Disease & Pest Explanation Function

## 1. Goal

Create a Python function that takes:

* A JSON string containing disease and pest information.
* A `detection_type` parameter: `"disease"` or `"pest"`.

The function should:

1. Select only the requested type.
2. Explain each piece of information individually.
3. Return the explanations as JSON so the frontend can easily display them.
4. Work with new fields without requiring constant code changes.

---

## 2. Function

```python
def explain_detection(json_text, detection_type):
    ...
```

### Example

```python
result = explain_detection(json_text, "disease")
```

or:

```python
result = explain_detection(json_text, "pest")
```

---

## 3. Input Example

```json
{
    "disease": {
        "name": "Rice Blast",
        "confidence": 0.94,
        "severity": "High",
        "risk": 0.82,
        "symptoms": [
            "Brown lesions",
            "Leaf damage"
        ],
        "weather": {
            "temperature": 28,
            "humidity": 85
        }
    },
    "pest": {
        "name": "Rice Stem Borer",
        "confidence": 0.89,
        "severity": "Medium"
    }
}
```

---

## 4. Important Requirement

The explanation should be generated **individually for every field**.

Instead of returning one large explanation like:

```text
Rice Blast was detected with 94% confidence and high severity...
```

the function should return structured JSON like:

```json
{
    "name": {
        "value": "Rice Blast",
        "explanation": "Rice Blast is the detected disease affecting the crop."
    },
    "confidence": {
        "value": 0.94,
        "explanation": "The model is 94% confident that the detected disease is Rice Blast."
    },
    "severity": {
        "value": "High",
        "explanation": "High severity means the disease may significantly affect the crop if not controlled."
    },
    "risk": {
        "value": 0.82,
        "explanation": "The current estimated disease risk is 82%."
    }
}
```

This makes the output much easier for the frontend to use.

For example, the frontend can display:

```text
Disease
Rice Blast
↓
Explanation
Rice Blast is the detected disease...
```

---

## 5. Disease / Pest Selection

When:

```python
detection_type = "disease"
```

only the `disease` object should be processed.

When:

```python
detection_type = "pest"
```

only the `pest` object should be processed.

The other category should be ignored.

---

## 6. Dynamic Fields

Do not hard-code only fields such as:

```text
name
confidence
severity
risk
```

The JSON may later contain:

```text
cause
spread_rate
forecast
treatment
recommendations
weather
rainfall
temperature
humidity
```

The function should dynamically process any new fields.

---

## 7. Nested Information

Nested objects should also receive individual explanations.

Example:

```json
{
    "weather": {
        "temperature": 28,
        "humidity": 85
    }
}
```

should become something like:

```json
{
    "weather": {
        "temperature": {
            "value": 28,
            "explanation": "The recorded temperature is 28°C."
        },
        "humidity": {
            "value": 85,
            "explanation": "The recorded humidity is 85%."
        }
    }
}
```

---

## 8. Lists

Lists should also be handled.

Example:

```json
{
    "symptoms": [
        "Brown lesions",
        "Leaf damage"
    ]
}
```

Output:

```json
{
    "symptoms": [
        {
            "value": "Brown lesions",
            "explanation": "Brown lesions are a visible symptom of the detected disease."
        },
        {
            "value": "Leaf damage",
            "explanation": "Leaf damage indicates that the crop is being affected."
        }
    ]
}
```

---

## 9. Missing Values

The function must safely handle:

```json
null
```

or Python:

```python
None
```

It should not crash.

Example:

```json
{
    "treatment": {
        "value": null,
        "explanation": "Treatment information is currently unavailable."
    }
}
```

---

## 10. Error Handling

### Invalid detection type

```python
explain_detection(json_text, "weather")
```

should return:

```json
{
    "error": "Invalid detection type. Use 'disease' or 'pest'."
}
```

### Invalid JSON

If the input cannot be parsed:

```json
{
    "error": "Invalid JSON data."
}
```

---

## 11. Recommended Output Structure

The final returned JSON should follow this general structure:

```json
{
    "type": "disease",
    "data": {
        "name": {
            "value": "Rice Blast",
            "explanation": "Rice Blast is the detected disease affecting the crop."
        },
        "confidence": {
            "value": 0.94,
            "explanation": "The model is 94% confident in this detection."
        },
        "severity": {
            "value": "High",
            "explanation": "The detected disease currently has a high severity level."
        }
    }
}
```

This structure should be consistent for both disease and pest.

---

## 12. Processing Flow

```text
JSON Input
    ↓
Parse JSON
    ↓
Check detection_type
    ↓
Select Disease / Pest
    ↓
Process every field
    ↓
Process nested objects and lists
    ↓
Generate individual explanations
    ↓
Return structured JSON
    ↓
Frontend displays each field separately
```

---

## 13. LLM Integration

The explanation generation can later use an LLM.

The Python function can:

```text
Receive JSON
    ↓
Select disease/pest
    ↓
Send each relevant field to LLM
    ↓
Generate explanation for each field
    ↓
Build final JSON
```

The LLM should return structured data, not one giant paragraph.

For example:

```json
{
    "name": {
        "value": "Rice Blast",
        "explanation": "Rice Blast is a fungal disease that affects rice plants."
    },
    "confidence": {
        "value": 0.94,
        "explanation": "The detection model has a 94% confidence level."
    }
}
```

---

## 14. Main Objective

The function should essentially work like:

```text
Input JSON
    ↓
Select Disease / Pest
    ↓
Explain EACH field individually
    ↓
Return JSON
```

The frontend can then easily access:

```javascript
data.name.explanation
data.confidence.explanation
data.severity.explanation
data.risk.explanation
```

This keeps the backend responsible for generating explanations while the frontend only needs to display them.
