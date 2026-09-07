import json
import re


VALID_DETECTION_TYPES = {"disease", "pest"}


def format_key(key):
    """Convert JSON keys into human-readable labels."""
    key = str(key)
    key = re.sub(r"([a-z])([A-Z])", r"\1 \2", key)
    key = key.replace("_", " ")
    return key.strip().capitalize()


def format_scalar(key, value):
    """Convert a simple value into a human-readable string with units."""

    if value is None:
        return "Unavailable"

    key_lower = str(key).lower()

    # Boolean values
    if isinstance(value, bool):
        return "Yes" if value else "No"

    # Numbers
    if isinstance(value, (int, float)):

        # Confidence / risk / probability
        if key_lower in {"confidence", "risk", "probability", "likelihood"}:
            if 0 <= value <= 1:
                return f"{value * 100:.1f}%"
            return f"{value}%"

        # Weather / agricultural units
        if "temperature" in key_lower:
            return f"{value} °C"

        if "humidity" in key_lower:
            return f"{value}%"

        if "precipitation" in key_lower or "rainfall" in key_lower:
            return f"{value} mm"

        if "wind_speed" in key_lower or "wind_gust" in key_lower:
            return f"{value} km/h"

        if "vpd" in key_lower or "vapour_pressure_deficit" in key_lower:
            return f"{value} kPa"

        if "evapotranspiration" in key_lower:
            return f"{value} mm"

        if "solar_radiation" in key_lower or "shortwave_radiation" in key_lower:
            return f"{value} W/m²"

        if "visibility" in key_lower:
            return f"{value} m"

        return str(value)

    return str(value)


def explain_scalar(key, value, detection_type):
    """Create a natural-language sentence for a simple field."""

    label = format_key(key)
    key_lower = str(key).lower()

    if value is None:
        return f"{label}: Information is unavailable."

    formatted_value = format_scalar(key, value)

    if key_lower == "name":
        return f"The detected {detection_type} is {value}."

    if key_lower == "confidence":
        return (
            f"The model's confidence in this "
            f"{detection_type} detection is {formatted_value}."
        )

    if key_lower == "severity":
        return f"The {detection_type} severity is classified as {value}."

    if key_lower == "risk":
        return (
            f"The estimated risk associated with this "
            f"{detection_type} is {formatted_value}."
        )

    if key_lower in {"symptom", "symptoms"}:
        return f"Symptoms: {formatted_value}"

    return f"{label}: {formatted_value}"


def explain_value(key, value, detection_type, level=0):
    """Recursively explain dictionaries, lists, and scalar values."""

    indent = "  " * level
    output = []

    # Dictionary
    if isinstance(value, dict):

        # Don't print a redundant top-level "Disease:" / "Pest:"
        if key:
            output.append(f"{indent}{format_key(key)}:")
            child_level = level + 1
        else:
            child_level = level

        for child_key, child_value in value.items():
            output.extend(
                explain_value(
                    child_key,
                    child_value,
                    detection_type,
                    child_level
                )
            )

        return output

    # List / array
    if isinstance(value, list):

        if key:
            output.append(f"{indent}{format_key(key)}:")

        if not value:
            output.append(f"{indent}  No information available.")
            return output

        for index, item in enumerate(value, start=1):

            # List containing dictionaries
            if isinstance(item, dict):

                output.append(f"{indent}  Item {index}:")

                for child_key, child_value in item.items():
                    output.extend(
                        explain_value(
                            child_key,
                            child_value,
                            detection_type,
                            level + 2
                        )
                    )

            # List containing lists
            elif isinstance(item, list):

                output.extend(
                    explain_value(
                        f"Item {index}",
                        item,
                        detection_type,
                        level + 1
                    )
                )

            # Normal list item
            else:
                output.append(
                    f"{indent}  {index}. {item}"
                )

        return output

    # Simple value
    output.append(
        f"{indent}{explain_scalar(key, value, detection_type)}"
    )

    return output


def explain_detection(json_text, detection_type):
    """
    Explain disease or pest information from a JSON string.

    Parameters:
        json_text (str):
            JSON-formatted string containing disease and pest data.

        detection_type (str):
            Must be either "disease" or "pest".

    Returns:
        str:
            Human-readable explanation of the requested detection.
    """

    # Validate detection type
    if not isinstance(detection_type, str):
        return (
            "Invalid detection type. "
            "Please select either 'disease' or 'pest'."
        )

    detection_type = detection_type.lower().strip()

    if detection_type not in VALID_DETECTION_TYPES:
        return (
            "Invalid detection type. "
            "Please select either 'disease' or 'pest'."
        )

    # Parse JSON
    try:
        data = json.loads(json_text)

    except (json.JSONDecodeError, TypeError):
        return (
            "Unable to process the provided data because "
            "the input is not valid JSON."
        )

    # JSON root must be an object
    if not isinstance(data, dict):
        return (
            "Unable to process the provided data because "
            "the JSON root must be an object."
        )

    # Select only the requested category
    detection_data = data.get(detection_type)

    if detection_data is None:
        return (
            f"No {detection_type} information was found "
            "in the provided JSON data."
        )

    # Generate explanation
    explanation = explain_value(
        None,
        detection_data,
        detection_type,
        level=0
    )

    # Add title
    result = [
        f"{detection_type.capitalize()} Detection Explanation",
        "=" * 32,
        ""
    ]

    result.extend(explanation)

    return "\n".join(result)


# ---------------------------------------------------------
# TESTING
# ---------------------------------------------------------

if __name__ == "__main__":

    sample_json = """
    {
        "disease": {
            "name": "Rice Blast",
            "confidence": 0.94,
            "severity": "High",
            "symptoms": [
                "Brown lesions",
                "Leaf damage"
            ],
            "weather_conditions": {
                "temperature": 28,
                "humidity": 85
            },
            "risk": 0.82,
            "recommendations": {
                "immediate_action": "Remove heavily infected leaves",
                "monitoring": "Check the field every 2 days"
            }
        },

        "pest": {
            "name": "Rice Stem Borer",
            "confidence": 0.89,
            "severity": "Medium",
            "symptoms": [
                "Dead hearts",
                "White ears"
            ],
            "risk": 0.64
        }
    }
    """

    print(explain_detection(sample_json, "disease"))

    print("\n" + "#" * 40 + "\n")

    print(explain_detection(sample_json, "pest"))