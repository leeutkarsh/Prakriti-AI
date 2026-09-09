# React UI Task

## Goal
Build the complete React + TypeScript frontend only. Streamlit/Python/model integration will be handled separately.

## Build
- Full UI/UX: image upload, preview, dropdowns, textarea, buttons, tabs/cards, loading, error, result, reset.
- Make the result screen complete, including the processed/annotated image.
- Use mock data so every UI state can be demonstrated without a backend.

## Inputs
Use meaningful names, not indexes:
- `selectedImage`
- `selectedCrop`
- `selectedPlantPart`
- `selectedSeason`
- `observedSymptoms`
- Add other fields with clear semantic names where needed.

Keep the values themselves meaningful, e.g. `"Tomato"`, `"Leaf"`, `"Summer"` — do NOT expose model/preprocessing indexes such as `0`, `1`, `2` as the frontend meaning.

## Results
Render everything dynamically from a result object. Example shape:

```ts
{
  diseaseName: "Early Blight",
  confidence: 94.2,
  severity: "Moderate",
  symptoms: ["Yellow spots", "Dark lesions"],
  recommendation: "Example recommendation",
  resultImage: "mock-image-url"
}
```

Do not hard-code prediction values directly into JSX.

## Image handling
- Use the browser file picker.
- Show image preview, filename, change/remove actions.
- Do NOT try to obtain the user's real local filesystem path.
- Keep the selected `File` available; Python will handle temporary file/path creation later.

## Code structure
Keep the UI modular with reusable components. Keep a clearly identifiable form/input state and result state so the Python/Streamlit integration can be added later without redesigning the UI.

## Do NOT build
- Python
- Streamlit integration
- FastAPI/API routes
- Model loading/inference
- YOLO/PyTorch
- Preprocessing/postprocessing
- Database/backend logic

## Deliver
- Complete React + TypeScript source
- `package.json`
- Build/run configuration
- Components and styles/assets
- Type definitions/interfaces
- Mock input/result data
- README with setup/run instructions

The final frontend should be a finished UI that I can later connect to Streamlit/Python by replacing the mock data/communication layer only.
