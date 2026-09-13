"""
viewer_server.py

A tiny local HTTP server with two jobs:

  1. Serve offline_field_viewer/ as static files (index.html, style.css,
     viewer.js, the model-viewer bundle, and the .glb) so a browser tab
     (or the iframe embedded in the Streamlit page) can load the existing
     3D viewer completely unchanged.

  2. Answer GET /gesture with the latest gesture command as JSON.
     offline_field_viewer/viewer.js already polls this exact endpoint
     every 35ms -- this server is the other half of a bridge whose
     protocol already existed in the viewer, not a new one invented here.

Runs entirely on 127.0.0.1 with no external network access, satisfying the
project's offline requirement. Started once per process from app.py in a
daemon thread so Streamlit's normal script-rerun behavior never tries to
bind the port twice.
"""

from __future__ import annotations

import logging
import threading

from flask import Flask, jsonify, send_from_directory

import config
from shared_state import gesture_state

_server_lock = threading.Lock()
_server_started = False


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    # Quiet Flask's per-request access log -- this endpoint is polled ~30x/sec.
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    @app.route("/gesture", methods=["GET"])
    def gesture():
        response = jsonify(gesture_state.get())
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def static_files(path):
        return send_from_directory(str(config.VIEWER_DIR), path)

    return app


def start_viewer_server_once() -> None:
    """Starts the Flask server in a background daemon thread, exactly once
    per process, regardless of how many times Streamlit re-runs this
    module's importing script."""

    global _server_started

    with _server_lock:
        if _server_started:
            return

        app = create_app()

        def _run():
            app.run(
                host=config.VIEWER_SERVER_HOST,
                port=config.VIEWER_SERVER_PORT,
                threaded=True,
                use_reloader=False,
                debug=False,
            )

        thread = threading.Thread(target=_run, name="viewer-http-server", daemon=True)
        thread.start()
        _server_started = True
