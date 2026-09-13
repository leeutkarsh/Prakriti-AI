"""
download_model.py

One-time setup step: downloads MediaPipe's official `hand_landmarker.task`
model file into models/, so gesture_detector.py can load it offline from
then on.

Why this exists instead of the model being bundled in the project already:
MediaPipe's current Tasks API (used by this project -- the older
`mediapipe.solutions.hands` API has been removed from recent MediaPipe
releases) loads its neural network from a `.task` file rather than
shipping it inside the `mediapipe` pip package. Google hosts the official
file; there is no legitimate way to vendor it into this repo without
fetching it from Google at least once.

This is exactly analogous to `pip install -r requirements.txt`: one
internet-connected step, run once, after which the whole application
(including this model) runs completely offline.

Usage:
    python download_model.py
"""

from __future__ import annotations

import sys
import urllib.error
import urllib.request

import config

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)


def main() -> int:
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    dest = config.HAND_LANDMARKER_MODEL_PATH

    if dest.is_file() and dest.stat().st_size > 0:
        print(f"Model already present at {dest} ({dest.stat().st_size:,} bytes). Nothing to do.")
        return 0

    print(f"Downloading MediaPipe HandLandmarker model to {dest} ...")
    print(f"Source: {MODEL_URL}")

    tmp_path = dest.with_suffix(".task.part")

    try:
        with urllib.request.urlopen(MODEL_URL, timeout=30) as response, open(tmp_path, "wb") as out_file:
            total = response.length
            downloaded = 0
            chunk_size = 1024 * 64

            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r  {downloaded:,} / {total:,} bytes ({pct:.0f}%)", end="", flush=True)
                else:
                    print(f"\r  {downloaded:,} bytes", end="", flush=True)

        print()
        tmp_path.replace(dest)

    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print()
        print(f"Download failed: {exc}")
        print(
            "No internet access right now? You only need this once. Either:\n"
            f"  - re-run this script when you have a connection, or\n"
            f"  - manually download the file from:\n      {MODEL_URL}\n"
            f"    and save it as:\n      {dest}"
        )
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        return 1

    print(f"Done. Saved {dest.stat().st_size:,} bytes to {dest}")
    print("The app can now run completely offline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
