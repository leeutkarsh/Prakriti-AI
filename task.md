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

## Results
Render everything dynamically from a result object. Example shape:
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

## Existing Starting UI

- There is already an existing starting/input UI with fields such as file upload, soil type, etc.
- Reuse/attach that existing UI instead of rebuilding it from scratch.
- Include all files/assets/components needed for that existing starting UI in the final handoff.
- Make sure the final project runs with that starting UI included and keeps its existing inputs/functionality intact.

## Deliver
- Complete React + TypeScript source
- `package.json`
- Build/run configuration
- Components and styles/assets
- Type definitions/interfaces
- Mock input/result data
- README with setup/run instructions

The final frontend should be a finished UI that I can later connect to Streamlit/Python by replacing the mock data/communication layer only.
