from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os

from MAIN import call_models

app = FastAPI()

ANNOTATION_PATHS = {}


@app.post("/analyze")
async def analyze(
    disease_or_pest: str = Form(...),
    address: str = Form(...),
    soil_type: str = Form(...),
    disease_category: str = Form(None),
    file: UploadFile = File(...)
):
    temp_path = None

    try:
        suffix = os.path.splitext(str(file.filename or ""))[1].lower()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:
            temp_path = temp_file.name

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        kb = call_models(
            disease_or_pest=disease_or_pest,
            address=address,
            soil_type=soil_type,
            filepath=temp_path,
            disease_category=disease_category
        )

        annotation_path = (
            kb.get("Disease Annotation Path")
            or kb.get("Pest Annotation Path")
        )

        annotated_image_url = None

        if annotation_path and os.path.exists(annotation_path):
            image_id = os.path.basename(annotation_path)
            ANNOTATION_PATHS[image_id] = annotation_path
            annotated_image_url = f"/annotated-images/{image_id}"

        return {
            "success": True,
            "data": kb,
            "annotated_image_url": annotated_image_url
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Analysis failed."
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/annotated-images/{image_id}")
async def get_annotated_image(image_id: str):
    image_path = ANNOTATION_PATHS.get(image_id)

    if not image_path or not os.path.exists(image_path):
        raise HTTPException(
            status_code=404,
            detail="Annotated image not found."
        )

    return FileResponse(image_path)