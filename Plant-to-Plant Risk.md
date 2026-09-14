# 🌱 Prakriti-AI — Plant-to-Plant Disease / Pest Risk

> **Visualizing how disease and pest risk can propagate between neighboring plants.**

Prakriti-AI's **Plant-to-Plant Disease / Pest Risk** feature transforms individual crop detections into a **field-level risk visualization**.

Instead of looking at plants as isolated detections, the system presents the field as a connected environment where an affected plant can increase the potential risk for plants in its immediate surroundings.

---

## 🌾 What Does It Show?

The feature presents a **top-down 2D view of an agricultural field**, with individual crops positioned in realistic planting rows.

Every plant is represented using a simple risk state:

| Status          | Meaning                                                               |
| --------------- | --------------------------------------------------------------------- |
| 🟢 **Healthy**  | Low estimated risk                                                    |
| 🟡 **At Risk**  | Elevated risk due to surrounding conditions or nearby affected plants |
| 🔴 **Affected** | Plant identified as affected by a disease or pest                     |

The field therefore becomes a visual map of **where problems exist and where they may potentially spread**.

---

## 🗺️ From Detection to Risk Map

A normal disease-detection system might simply report:

> **Rice Blast detected on Plant #482**

Prakriti-AI extends that idea by asking:

> **What about the plants surrounding Plant #482?**

The visualization creates a spatial relationship between plants.

```text
                  🟢
            🟢    🟡    🟢
        🟢   🟡    🔴    🟡   🟢
            🟢    🟡    🟢
                  🟢
```

The affected plant becomes the center of a **local risk zone**, while nearby plants receive progressively higher or lower risk depending on their spatial relationship with the affected area.

---

## 🔴 Risk Propagation

The core concept is based on **spatial proximity**.

An affected plant can act as a local source of potential risk.

```text
Affected Plant
      │
      ▼
Nearby Plants
      │
      ▼
Higher Estimated Risk
      │
      ▼
Visible Risk Cluster
```

The visual intensity decreases as the distance from the affected plant increases.

This produces the intuitive transition:

**🟢 Green → 🟡 Yellow → 🔴 Red**

where:

* **Green** represents low risk.
* **Yellow** represents elevated or emerging risk.
* **Red** represents high risk or an already affected plant.

---

## 🌱 Why Plant-to-Plant Risk?

Agricultural problems are rarely completely isolated.

Neighboring plants can experience similar:

* environmental conditions
* moisture levels
* canopy conditions
* pest exposure
* local soil conditions
* disease pressure

Because of this, a single detected problem can be more meaningful when viewed together with the plants around it.

The feature demonstrates the transition from:

```text
Individual Detection
        ↓
Plant-Level Risk
        ↓
Neighboring Plant Risk
        ↓
Field-Level Risk
```

This creates a more understandable picture of the condition of the field.

---

## 🖱️ Interactive Field Exploration

The field is designed to be explored naturally using the mouse.

### Hover

Moving across the field visually focuses the area around the cursor, making nearby plants and risk zones easier to inspect.

### Select a Plant

Selecting an individual crop reveals its detailed information.

For example:

```text
Plant #482

Disease / Pest
Rice Blast

Risk Level
High

Confidence
87%

Nearby Plants at Risk
14
```

This connects the individual plant to its surrounding risk environment.

### Explore the Field

The map can be navigated and inspected to understand how risk is distributed across different regions of the field.

---

## 📊 Field-Level Overview

Alongside the field map, the interface provides a summarized view of the overall crop condition.

Typical indicators include:

### 🌿 Healthy

Plants currently considered to have low estimated risk.

### ⚠️ At Risk

Plants located within elevated-risk areas or influenced by nearby affected plants.

### 🔴 Affected

Plants already associated with a detected disease or pest problem.

Together, these values provide a quick snapshot of the field while the map shows **where those plants are located**.

---

## 🔍 Plant-Level Intelligence

The selected-plant view makes the visualization more informative than a simple heatmap.

A plant can be associated with information such as:

```text
Plant ID
Disease / Pest
Risk Level
Detection Confidence
Nearby Plants at Risk
Field Location
```

For example:

> **Rice Blast detected with 87% confidence.
> 14 nearby plants are currently within the elevated-risk zone.**

This allows the user to move from a **field overview** to a **specific plant** in seconds.

---

## 🧠 How the Concept Works

Each plant can be thought of as having a small collection of information:

```text
Plant
├── Position
├── Crop Type
├── Health State
├── Risk Score
├── Disease / Pest
└── Nearby Risk
```

Affected plants become sources of spatial influence.

Plants closer to affected areas receive a stronger risk influence, while plants farther away receive a weaker influence.

Conceptually:

```text
Risk ≈ Base Risk + Local Influence − Distance Effect
```

The resulting risk score is then represented visually.

```text
Low Risk       → 🟢
Medium Risk    → 🟡
High Risk      → 🔴
Affected       → 🔴 + highlighted source
```

The result is a field map where disease and pest risk forms **visible spatial clusters** instead of appearing as disconnected detections.

---

## 🌍 From Crop Detection to Field Intelligence

The feature demonstrates a broader idea behind Prakriti-AI:

```text
        Crop Observation
               ↓
       Disease / Pest Detection
               ↓
          Plant Risk
               ↓
     Neighboring Plant Analysis
               ↓
        Spatial Risk Map
               ↓
      Field-Level Intelligence
```

The important shift is from:

> **“Which plant is affected?”**

to:

> **“Where is the problem, how concentrated is it, and which surrounding plants may require attention?”**

---

## ✨ Why This Visualization Matters

A conventional detection output may look like:

```text
Plant 118 → Healthy
Plant 119 → Healthy
Plant 120 → Rice Blast
Plant 121 → High Risk
Plant 122 → High Risk
Plant 123 → Healthy
```

The same information becomes much easier to understand when represented spatially:

```text
🟢 🟢 🟡 🟡 🟢
🟢 🟡 🔴 🟡 🟢
🟢 🟡 🔴 🟡 🟢
🟢 🟢 🟡 🟢 🟢
```

The **location, concentration, and relationship between plants** become immediately visible.

---

## 🚜 What This Demonstrates

The feature is a visual demonstration of how Prakriti-AI can move beyond isolated disease and pest detection to provide a **field-level understanding of crop health**.

It demonstrates:

* **Individual plant detection**
* **Plant-level risk estimation**
* **Spatial relationships between neighboring plants**
* **Potential risk propagation**
* **Affected-area visualization**
* **Field-level statistics**
* **Interactive plant inspection**
* **Localized risk clusters**

The field shown in the demonstration is synthetic, allowing the concept to be presented clearly while keeping the interface focused on the underlying idea.

---

## 🌿 The Bigger Idea

### **Detect the problem.**

### **Understand the neighborhood.**

### **Visualize the risk.**

### **Act before it spreads.**

Prakriti-AI's **Plant-to-Plant Disease / Pest Risk** view turns individual crop observations into a visual representation of the broader field environment.

It demonstrates how agricultural intelligence can move from **detecting a problem** to **understanding its spatial impact**.

---

### 🌱 Prakriti-AI

**Smarter Insights. Healthier Crops.**
