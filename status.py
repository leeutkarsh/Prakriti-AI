import json
from pathlib import Path

STATUS_FILE = Path(__file__).resolve().parent / "status.json"


def update_status(status, step, message):
    status_data = {
        "status": status,
        "step": step,
        "message": message
    }

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status_data, f)

    print("UPDATED:", status_data, flush=True)


def get_status():
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

            if not content:
                return {
                    "status": "idle",
                    "step": "waiting",
                    "message": "Waiting for analysis"
                }

            return json.loads(content)

    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "status": "idle",
            "step": "waiting",
            "message": "Waiting for analysis"
        }