from ultralytics import YOLO
import os

path = "best.pt"

if os.path.exists(path):
    model = YOLO(path)

    def disease_detection(file_path):
        detection = []

        results = model.predict(
            source=file_path,
            save=True,
            verbose=False,
            conf=0.25
        )

        for result in results:

            if len(result.boxes) == 0:
                continue

            kvp = {
                "disease_name": result.names[int(result.boxes.cls[0])],
                "saved_path": str(result.save_dir),
                "confidence": round(
                    float(result.boxes.conf[0]) * 100, 2
                )
            }

            detection.append(kvp)

        return detection
