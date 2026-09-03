## 1. What are we building?

We need to build one feature for our agriculture project:

> **Detect whether multiple farmers are reporting the same disease or pest in the same region.**

The system will receive information from a farmer/report, save it in **Supabase**, then use **Python functions** to search the stored reports and check whether there is an outbreak.

The important part is:

* **Python will contain all the logic.**
* **Supabase will only store and return the data through its API.**
* We are **NOT creating a Supabase/PostgreSQL function.**

### Simple flow

```text
Farmer / UI
    ↓
Select: Disease or Pest
    ↓
Enter disease/pest name
    ↓
Enter environmental information
    ↓
Python function
    ↓
Save report to Supabase
    ↓
Search previous reports
    ↓
Check same region + same disease/pest + risk score
    ↓
Is there an outbreak?
    ↓
YES → return matching reports
NO  → return []
```

# 3. Supabase Table

Create a table named:

```text
crop_reports
```

Keep the table simple.

| Column             | Type      | Meaning                           |
| ------------------ | --------- | --------------------------------- |
| `id`               | uuid      | Unique ID for each report         |
| `region`           | text      | Region where the report came from |
| `detection_type`   | text      | `Disease` or `Pest`               |
| `disease_pest`     | text      | Name of the disease or pest       |
| `temperature`      | float     | Air temperature in °C             |
| `humidity`         | float     | Humidity percentage               |
| `soil_temperature` | float     | Soil temperature in °C            |
| `soil_moisture`    | float     | Soil moisture percentage          |
| `rainfall`         | float     | Rainfall in mm                    |
| `risk_score`       | float     | AI-predicted risk score           |
| `reported_at`      | timestamp | Date and time of the report       |

---

# 4. Example Record

A disease report could look like:

```json
{
    "region": "Bhopal",
    "detection_type": "Disease",
    "disease_pest": "Rice Blast",
    "temperature": 28.5,
    "humidity": 82.0,
    "soil_temperature": 25.3,
    "soil_moisture": 67.0,
    "rainfall": 12.5,
    "risk_score": 0.91
}
```

A pest report could look like:

```json
{
    "region": "Bhopal",
    "detection_type": "Pest",
    "disease_pest": "Stem Borer",
    "temperature": 29.2,
    "humidity": 79.0,
    "soil_temperature": 26.1,
    "soil_moisture": 64.0,
    "rainfall": 8.4,
    "risk_score": 0.84
}
```

---

# 5. Python Functions

Create the following two Python functions:

```python
def save_report(
    region,
    detection_type,
    disease_pest,
    temperature,
    humidity,
    soil_temperature,
    soil_moisture,
    rainfall,
    risk_score
):
    pass
```

and:

```python
def search_outbreak(
    region,
    detection_type,
    disease_pest
):
    pass
```

The `search_outbreak()` function can use the information already stored in Supabase to find matching reports.

---

# 6. `save_report()`

Create a Python function named **`save_report()`**.

It should:

1. Take all the report values as parameters.
2. Create a dictionary containing those values.
3. Send the dictionary to the **Supabase cloud database using the Supabase API**.
4. Save the report inside the `crop_reports` table.

Example:

```python
def save_report(
    region,
    detection_type,
    disease_pest,
    temperature,
    humidity,
    soil_temperature,
    soil_moisture,
    rainfall,
    risk_score
):
    report = {
        "region": region,
        "detection_type": detection_type,
        "disease_pest": disease_pest,
        "temperature": temperature,
        "humidity": humidity,
        "soil_temperature": soil_temperature,
        "soil_moisture": soil_moisture,
        "rainfall": rainfall,
        "risk_score": risk_score
    }

    supabase.table("crop_reports").insert(report).execute()
```

The important idea is:

```text
Python
   ↓
save_report()
   ↓
Supabase API
   ↓
crop_reports table
```

---

# 7. `search_outbreak()`

Create a Python function named **`search_outbreak()`**.

It should search Supabase for reports having:

```text
same region
+
same disease/pest
+
risk score above 25%
```

For the prototype:

```text
25% = 0.25
```

So a report with:

```text
risk_score = 0.40
```

is considered.

But:

```text
risk_score = 0.20
```

is not considered.

The function should search for reports matching the same:

```text
region
detection_type
disease_pest
```

Example search:

```python
response = (
    supabase
    .table("crop_reports")
    .select("*")
    .eq("region", region)
    .eq("detection_type", detection_type)
    .eq("disease_pest", disease_pest)
    .execute()
)

reports = response.data
```

Then filter the reports by the 25% risk threshold.

Example:

```python
valid_reports = [
    report
    for report in reports
    if report["risk_score"] > 0.25
]
```

---

# 8. Outbreak Condition

After filtering the reports, count them.

The rule is:

```text
More than 10 matching reports
        ↓
Possible outbreak
```

So:

```python
if len(valid_reports) > 10:
    # outbreak
```

If there are 10 or fewer:

```python
return []
```

### Examples

```text
5 matching reports
→ no outbreak
→ []

10 matching reports
→ no outbreak
→ []

11 matching reports
→ outbreak detected
→ return outbreak data
```

---

# 9. What should `search_outbreak()` return?

When there is **no outbreak**, return:

```python
[]
```

When there **is an outbreak**, return a JSON-compatible dictionary/list containing the required outbreak information.

The returned outbreak data should contain:

```text
region
detected pest/disease
pest/disease name
average temperature
average humidity
average rainfall
average soil moisture
average soil temperature
risk score
```

For the environmental values, calculate the **average** of the matching reports.

For example:

```text
11 matching reports

Average temperature      → 28.6
Average humidity         → 81.4
Average rainfall         → 13.7
Average soil moisture    → 66.2
Average soil temperature → 25.4
```

---

# 10. Example Output

If an outbreak is detected, the result can look like:

```json
{
    "region": "Bhopal",
    "detection_type": "Disease",
    "disease_pest": "Rice Blast",
    "average_temperature": 28.6,
    "average_humidity": 81.4,
    "average_rainfall": 13.7,
    "average_soil_moisture": 66.2,
    "average_soil_temperature": 25.4,
    "average_risk_score": 0.87,
    "report_count": 11
}
```

The `report_count` is useful because it tells us how many reports were used to detect the outbreak.

---

# 11. Example of Calculating Averages

Python can calculate averages using `sum()` and `len()`.

For example:

```python
average_temperature = (
    sum(report["temperature"] for report in valid_reports)
    / len(valid_reports)
)
```

The same approach can be used for:

```python
humidity
rainfall
soil_moisture
soil_temperature
risk_score
```

---

# 12. Important Example — Disease vs Pest

The `detection_type` must be used when searching.

Example:

```text
Bhopal | Disease | Rice Blast
Bhopal | Disease | Rice Blast
Bhopal | Disease | Rice Blast

Bhopal | Pest | Stem Borer
Bhopal | Pest | Stem Borer
```

A search for:

```text
Bhopal
Disease
Rice Blast
```

must only consider:

```text
Bhopal | Disease | Rice Blast
```

Do not mix disease reports with pest reports.

---

# 13. Important Example — Different Regions

Suppose the database contains:

```text
Bhopal | Disease | Rice Blast
Bhopal | Disease | Rice Blast
Indore | Disease | Rice Blast
Indore | Disease | Rice Blast
```

A Bhopal search should only use the Bhopal reports.

Do not combine reports from different regions.

---

# 14. Full Example of `search_outbreak()`

This shows the basic logic:

```python
def search_outbreak(region, detection_type, disease_pest):

    response = (
        supabase
        .table("crop_reports")
        .select("*")
        .eq("region", region)
        .eq("detection_type", detection_type)
        .eq("disease_pest", disease_pest)
        .execute()
    )

    reports = response.data

    # Keep reports with risk score above 25%
    valid_reports = [
        report
        for report in reports
        if report["risk_score"] > 0.25
    ]

    # More than 10 reports = possible outbreak
    if len(valid_reports) <= 10:
        return []

    average_temperature = (
        sum(r["temperature"] for r in valid_reports)
        / len(valid_reports)
    )

    average_humidity = (
        sum(r["humidity"] for r in valid_reports)
        / len(valid_reports)
    )

    average_rainfall = (
        sum(r["rainfall"] for r in valid_reports)
        / len(valid_reports)
    )

    average_soil_moisture = (
        sum(r["soil_moisture"] for r in valid_reports)
        / len(valid_reports)
    )

    average_soil_temperature = (
        sum(r["soil_temperature"] for r in valid_reports)
        / len(valid_reports)
    )

    average_risk_score = (
        sum(r["risk_score"] for r in valid_reports)
        / len(valid_reports)
    )

    return {
        "region": region,
        "detection_type": detection_type,
        "disease_pest": disease_pest,
        "average_temperature": average_temperature,
        "average_humidity": average_humidity,
        "average_rainfall": average_rainfall,
        "average_soil_moisture": average_soil_moisture,
        "average_soil_temperature": average_soil_temperature,
        "average_risk_score": average_risk_score,
        "report_count": len(valid_reports)
    }
```

This is an example of the required logic. Improve the code where necessary, but keep the overall behavior the same.

---

# 15. Example Usage

First save a new report:

```python
save_report(
    "Bhopal",
    "Disease",
    "Rice Blast",
    28.5,
    82.0,
    25.3,
    67.0,
    12.5,
    0.91
)
```

Then search for an outbreak:

```python
result = search_outbreak(
    "Bhopal",
    "Disease",
    "Rice Blast"
)

print(result)
```

Possible result:

```python
[]
```

or:

```python
{
    "region": "Bhopal",
    "detection_type": "Disease",
    "disease_pest": "Rice Blast",
    "average_temperature": 28.6,
    "average_humidity": 81.4,
    "average_rainfall": 13.7,
    "average_soil_moisture": 66.2,
    "average_soil_temperature": 25.4,
    "average_risk_score": 0.87,
    "report_count": 11
}
```

---

# 16. Final Architecture

Keep the architecture simple:

```text
UI
 ↓
User selects Disease / Pest
 ↓
Python
 ↓
save_report()
 ↓
Supabase API
 ↓
Database


Python
 ↓
search_outbreak()
 ↓
Supabase API
 ↓
Search reports
 ↓
Filter risk > 25%
 ↓
Count reports
 ↓
> 10 reports?
 ↓
YES → calculate averages + return JSON-compatible result
NO  → return []
```

---

# 🎯 Final Goal

Build **two Python functions**:

```python
save_report()
search_outbreak()
```

### `save_report()`

Takes all the report values and saves them to Supabase through the API.

### `search_outbreak()`

Takes:

```text
region
detection_type
disease_pest
```

Then:

```text
Search Supabase
      ↓
Find same region + same disease/pest
      ↓
Keep risk_score > 0.25
      ↓
Count reports
      ↓
More than 10?
      ↓
YES → calculate averages and return outbreak JSON
NO  → return []
```
