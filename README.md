# SLIDE 1 — PROPOSED SOLUTION

## **Prakriti AI — From Detection to Prevention**

### **What it does**

An AI-powered agricultural platform that detects **plant diseases and pests**, predicts their **spread risk**, visualizes the entire farm in **3D**, and provides **early regional outbreak alerts**.

### **How it works**

**Farmer Input → Detection → Environment Analysis → Risk Prediction → Recommendation → Alert**

* Detects diseases/pests from plant images using **YOLO-based models**.
* Supports **Rice, Wheat & 116+ crop categories**.
* Uses **location + historical/forecast weather + predicted soil characteristics** to calculate environmental risk.
* Provides **fertilizer and crop recommendations**.
* Generates simplified explanations of complex model results.

### **Key Innovation**

**1. Plant-to-Plant Risk Mapping**
Calculates how many nearby plants may be at risk of the detected disease/pest, helping identify potential spread zones.

**2. Video → 3D Farm Digital Twin**
Drone videos/images are converted into a **3D reconstruction of the farm** using COLMAP, allowing users to view the farm spatially and identify affected areas.

**3. Regional Outbreak Intelligence**
When **10+ farmers in the same region** report the same disease/pest with **risk >25%**, the system triggers an outbreak warning and shares recommended action.

**4. Farm-Level Risk Visualization**
Instead of showing only *“Disease Detected”*, the system answers:
**Where is it? → How risky is it? → What could spread? → What should the farmer do?**

---

# SLIDE 2 — TECHNOLOGIES & METHODOLOGY

## **Technology Stack**

**AI/ML:** YOLO • XGBoost • Random Forest • ResNet50
**Data & Training:** Label Studio • Google Colab • Feature Engineering
**Computer Vision:** OpenCV
**3D Reconstruction:** COLMAP • SfM • MVS
**Backend:** FastAPI • REST APIs
**Weather:** Open-Meteo
**AI Explanation:** NVIDIA API

### **Core Processing Pipeline**

**Farmer Input**
↓
**Image + Crop + Disease/Pest + Soil Type + Address**
↓
**YOLO Disease/Pest Detection**
↓
**Address → Latitude/Longitude**
↓
**Weather Analysis**

* Historical weather
* Forecast weather

↓
**Soil Characteristic Prediction**

* Latitude/Longitude
* Random Forest

↓
**Environmental & Spread Risk Analysis**
↓
**Risk Score**
↓
**Fertilizer / Crop Recommendation**
↓
**AI Simplified Explanation**

### **3D Digital Farm Pipeline**

**Drone Video / Images**
→ **Frame Extraction**
→ **Structure from Motion (SfM)**
→ **Camera Pose + Sparse 3D**
→ **Multi-View Stereo (MVS)**
→ **Dense 3D Farm Reconstruction**

---

# SLIDE 3 — FEASIBILITY, CHALLENGES & SOLUTIONS

## **Why Prakriti AI is Feasible**

* Built using **established ML and computer-vision frameworks**.
* Uses agricultural datasets combined with **real weather data**.
* Modular **FastAPI architecture** allows models to be improved independently.
* 3D reconstruction works from **drone/video imagery**, reducing the need for specialized field mapping hardware.

### **Challenges → Our Approach**

| Challenge                           | Approach                                                 |
| ----------------------------------- | -------------------------------------------------------- |
| Diverse crop diseases               | Multiple crop-specific YOLO models + **116+ categories** |
| Limited/varied training data        | Dataset combination + **Label Studio annotation**        |
| Weather affects disease risk        | Historical + forecast weather features                   |
| Soil information may be unavailable | **Location-based soil prediction**                       |
| False outbreak alerts               | Risk threshold + multiple farmer reports                 |
| Large farm visualization            | **3D reconstruction + spatial visualization**            |
| Complex AI outputs                  | NVIDIA-powered simplified explanations                   |

### **Architecture Advantage**

**Detection → Environment → Risk → Recommendation → Alert**

Each stage can be independently upgraded without redesigning the entire system.

---

# SLIDE 4 — POTENTIAL IMPACT

## **From Individual Detection to Community Protection**

### **For Farmers**

**Early Detection**
Identify threats before they spread widely.

**Targeted Action**
See affected/risky areas instead of treating the entire farm blindly.

**Better Decisions**
Weather + soil + disease information combined into one risk assessment.

**Actionable Recommendations**
Fertilizer, crop and preventive recommendations in simple language.

### **For the Environment**

* Supports **precision agriculture**.
* Can reduce unnecessary pesticide/fertilizer application.
* Encourages targeted intervention instead of blanket treatment.

### **For the Agricultural Community**

A farm no longer works as an isolated unit.

**Farmer A + Farmer B + Farmer C + …**
↓
**Regional Disease/Pest Pattern**
↓
**Early Outbreak Alert**
↓
**Collective Prevention**

### **Impact Vision**

> **Detect early. Predict spread. Visualize the farm. Warn the community. Prevent losses.**

---

# SLIDE 5 — REFERENCES & RESEARCH

## **Datasets, APIs & Research Resources**

### **Disease & Pest**

**Hugging Face — PlantDiseaseDetection**
JK-TK/PlantDiseaseDetection

**Pestopia Dataset**
https://www.kaggle.com/datasets/shruthisindhura/pestopia

**Rice Disease Dataset**
https://www.kaggle.com/datasets/nischallal/rice-disease-dataset

**Wheat Disease Dataset**
https://www.kaggle.com/datasets/yasserhessein/wheat-disease-dataset-small

### **Soil / Crop / Fertilizer**

**Soil Nutrient Dataset**
https://www.kaggle.com/datasets/manojk2002/soil-nutrient-dataset-of-southern-indian-states

**Crop Recommendation Dataset**
https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset/data

**Fertilizer Recommendation Dataset**
https://www.kaggle.com/datasets/miadul/fertilizer-recommendation-dataset

### **External Resources**

**Open-Meteo Weather API**
https://open-meteo.com/

**Training / Supporting Resources**
https://drive.google.com/drive/folders/1MTfO3zq6BkJfhzQqxoNblQuQealdSs9U

### **Major Methods**

**YOLO • ResNet50 • XGBoost • Random Forest • Label Studio • COLMAP • SfM • MVS • Statistical Feature Engineering**
