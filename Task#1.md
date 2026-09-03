# 🌾 Prakriti AI UI

>**note**: *You can change title of page and fields according to your choice which suits best.*

## 🌱 1. Purpose

Build the **frontend UI only** for the Agriculture Disease & Pest Reporting feature using **React.js**.

The frontend will later communicate with the Python **FastAPI backend through REST APIs**, but **API integration is NOT part of the current task**.

For now, the goal is to create a **clean, attractive, responsive form** where a farmer can submit information about a crop disease or pest problem.

---

# 📝 3. Main Form

The frontend should contain a main form titled:

## **Report Crop Disease / Pest**

The form should contain the following fields:

| # | Field             | Input Type   | Required |
| - | ----------------- | ------------ | -------- |
| 1 | Upload Crop Image | Image Upload | ✅        |
| 2 | Select Crop       | Dropdown     | ✅        |
| 3 | Issue Type        | Dropdown     | ✅        |
| 4 | Select State      | Dropdown     | ✅        |
| 5 | Farmer Address    | Textarea     | ✅        |
| 6 | Soil Type         | Dropdown     | ✅        |

---

# 📷 4. Field 1 — Photo Upload

### Label

```text
Upload Crop Image
```

### Input

Image upload field.

### Accepted Formats

```text
.png
.jpg
.jpeg
.webp
```

Other common image formats may also be accepted where supported by the browser.

### UI Requirements

The farmer should be able to:

* Click to upload an image
* Select an image from their device
* See the selected image as a preview
* Remove/change the selected image

### Before Upload

```text
┌─────────────────────────────────────────┐
│                                         │
│            📷 Upload Crop Image        │
│                                         │
│       Click to select an image          │
│       PNG, JPG, JPEG, WEBP              │
│                                         │
└─────────────────────────────────────────┘
```

### After Upload

```text
┌─────────────────────────────────────────┐
│                                         │
│             [Image Preview]             │
│                                         │
│          ✓ image_name.jpg               │
│                                         │
│          [ Change Image ]               │
│                                         │
└─────────────────────────────────────────┘
```

### Validation

The user should **not** be able to submit the form without an image.

---

# 🌾 5. Field 2 — Crop Selection

### Label

```text
Select Crop
```

### Input

Dropdown / selectbox.

### Options

```text
Wheat
Rice
Other
```

### Initial Value

```text
Select Crop
```

The dropdown should initially show the placeholder rather than automatically selecting a crop.

---

# 🦠 6. Field 3 — Disease / Pest Selection

### Label

```text
Issue Type
```

### Input

Dropdown / selectbox.

### Options

```text
Disease
Pest
```

### Initial Value

```text
Select Disease / Pest
```

This field determines whether the reported agricultural problem is a:

* **Disease**
* **Pest infestation**

---

# 🇮🇳 7. Field 4 — Region / State

### Label

```text
Select State
```

### Input

Dropdown / selectbox.

The dropdown should contain the names of **all Indian states**.

### Example

```text
Select State

Andhra Pradesh
Arunachal Pradesh
Assam
Bihar
Chhattisgarh
Goa
Gujar...
```

The farmer will select the state/region in which they are located.

---

# 📍 8. Field 5 — Address

### Label

```text
Farmer Address
```

### Input

TextArea or large text input.

### Placeholder

```text
Enter your farming/location address
```

The farmer should provide their **address**.

---

# 🌱 9. Field 6 — Soil Type

### Label

```text
Soil Type
```

### Input

Dropdown / selectbox.

### Options

```text
Select Soil Type

Clayey
Sandy
Black
Red
Loamy
```

The initial value should be:

```text
Select Soil Type
```

---

# 🚀 10. Submit Button

At the bottom of the form:

```text
┌───────────────────────────┐
│      Submit Report        │
└───────────────────────────┘
```

For the **frontend-only stage**, clicking the button does **not** need to call FastAPI.

Instead, it can:

1. Validate the form
2. Display validation errors
3. Display the submitted values in the console or temporary UI
4. Show a temporary success message

### Example Success Message

```text
✅ Report information collected successfully.
```

> The actual API request will be implemented later.

---

# ✅ 11. Frontend Validation

The following fields should be required:

```text
✓ Crop
✓ Photo
✓ Disease / Pest Type
✓ State
✓ Address
✓ Soil Type
```

The frontend should **prevent submission when a required field is missing**.

### Example Validation Messages

```text
⚠ Please upload a crop image.

⚠ Please select a crop.

⚠ Please select an issue type.

⚠ Please select your region.

⚠ Please enter your address.

⚠ Please select the soil type.
```

Validation messages should appear **close to the relevant field**.

---

# ✨ 13. UX Requirements

The interface should be:

* **Simple**
* **Clean**
* **Farmer-friendly**
* **Easy to understand**
* **Mobile-friendly**
* **Visually consistent**
* **Fast to interact with**

The design should prioritize **clarity and ease of use** over unnecessary complexity.

---

# ✅ 15. Definition of Done

The frontend task is complete when:

```text
[✓] Farmer can upload an image
[✓] Farmer can preview the image
[✓] Farmer can select a crop
[✓] Farmer can select Disease/Pest
[✓] Farmer can select an Indian state/region
[✓] Farmer can enter an address
[✓] Farmer can select soil type
[✓] Required fields are validated
[✓] Form is responsive
[✓] UI is ready for future REST API integration with Fast API
```

---

# 🎯 Current Objective

> ## **Build only this frontend 1st.**

The current goal is to create and finalize the **React.js user interface**.

**Do not implement backend/API functionality at this stage.**
