const viewer = document.getElementById("fieldViewer");
const statusEl = document.getElementById("status");
const errorEl = document.getElementById("error");
const resetButton = document.getElementById("reset");
const fullscreenButton = document.getElementById("fullscreen");


// ============================================================
// PERFECT ORIGINAL CAMERA
// ============================================================

const CAMERA = {
    orbit: "1.271deg 180.000deg 106.6765m",
    target: "3.5193m 44.1891m 2.1837m",
    fov: "25.158deg"
};


// ============================================================
// GESTURE CONTROL
// ============================================================

const GESTURE_ENDPOINT = "/gesture";


// Rotation sensitivity.
//
// Small number = slow/smooth.
// Large number = aggressive.
//
// This is intentionally moderate.
const ROTATE_SENSITIVITY = 5.2;


// Pinch zoom sensitivity.
const ZOOM_SENSITIVITY = 42.0;


// Camera limits.
const MIN_RADIUS = 35.0;
const MAX_RADIUS = 180.0;


// Vertical orbit limits.
const MIN_PHI = 0.0873;
const MAX_PHI = 3.0543;


// ============================================================
// STATE
// ============================================================

let lastGesture = "none";

let lastRotateX = null;
let lastRotateY = null;

let lastPinchDistance = null;

let lastGestureTimestamp = 0;


// ============================================================
// RESET
// ============================================================

function resetCamera() {

    if (!viewer) {
        return;
    }

    viewer.cameraOrbit = CAMERA.orbit;
    viewer.cameraTarget = CAMERA.target;
    viewer.fieldOfView = CAMERA.fov;
}


if (resetButton) {

    resetButton.addEventListener(
        "click",
        resetCamera
    );
}


// ============================================================
// FULLSCREEN
// ============================================================

if (fullscreenButton) {

    fullscreenButton.addEventListener(
        "click",
        async () => {

            try {

                if (document.fullscreenElement) {

                    await document.exitFullscreen();

                } else {

                    await document.documentElement.requestFullscreen();

                }

            } catch (error) {

                console.warn(
                    "Fullscreen unavailable:",
                    error
                );
            }
        }
    );
}


// ============================================================
// MODEL EVENTS
// ============================================================

if (viewer) {

    viewer.addEventListener(
        "load",
        () => {

            if (statusEl) {

                statusEl.textContent =
                    "MODEL READY • GESTURE CONTROL";
            }

            if (errorEl) {

                errorEl.classList.add(
                    "hidden"
                );
            }

            resetCamera();
        }
    );


    viewer.addEventListener(
        "error",
        () => {

            if (statusEl) {

                statusEl.textContent =
                    "MODEL LOAD ERROR";
            }

            if (errorEl) {

                errorEl.classList.remove(
                    "hidden"
                );
            }
        }
    );
}


// ============================================================
// NORMALIZE POINT
// ============================================================

function clamp(value, min, max) {

    return Math.max(
        min,
        Math.min(max, value)
    );
}


// ============================================================
// ROTATION
// ============================================================

function handleRotation(data) {

    const x = Number(data.point_x);
    const y = Number(data.point_y);

    if (
        !Number.isFinite(x) ||
        !Number.isFinite(y)
    ) {
        return;
    }


    // First frame after starting rotation.
    if (
        lastRotateX === null ||
        lastRotateY === null
    ) {

        lastRotateX = x;
        lastRotateY = y;

        return;
    }


    const dx = x - lastRotateX;
    const dy = y - lastRotateY;


    lastRotateX = x;
    lastRotateY = y;


    // Ignore microscopic MediaPipe noise.
    if (
        Math.abs(dx) < 0.0008 &&
        Math.abs(dy) < 0.0008
    ) {
        return;
    }


    const orbit = viewer.getCameraOrbit();


    // Horizontal hand movement
    // → horizontal camera rotation.
    orbit.theta += (
        dx * ROTATE_SENSITIVITY
    );


    // Vertical hand movement
    // → vertical camera rotation.
    orbit.phi -= (
        dy * ROTATE_SENSITIVITY
    );


    orbit.phi = clamp(
        orbit.phi,
        MIN_PHI,
        MAX_PHI
    );


    orbit.radius = clamp(
        orbit.radius,
        MIN_RADIUS,
        MAX_RADIUS
    );


    viewer.cameraOrbit =
        `${orbit.theta}rad ` +
        `${orbit.phi}rad ` +
        `${orbit.radius}m`;
}


// ============================================================
// PINCH ZOOM
// ============================================================

function handlePinch(data) {

    const currentDistance =
        Number(data.normalized_distance);


    if (
        !Number.isFinite(currentDistance)
    ) {
        return;
    }


    if (lastPinchDistance === null) {

        lastPinchDistance =
            currentDistance;

        return;
    }


    const delta =
        currentDistance -
        lastPinchDistance;


    lastPinchDistance =
        currentDistance;


    // Ignore tiny hand tracking noise.
    if (Math.abs(delta) < 0.001) {
        return;
    }


    const orbit =
        viewer.getCameraOrbit();


    /*
        Fingers moving apart:

            delta > 0

        → zoom IN
        → camera radius gets smaller.


        Fingers moving together:

            delta < 0

        → zoom OUT
        → camera radius gets larger.
    */

    orbit.radius -= (
        delta * ZOOM_SENSITIVITY
    );


    orbit.radius = clamp(
        orbit.radius,
        MIN_RADIUS,
        MAX_RADIUS
    );


    viewer.cameraOrbit =
        `${orbit.theta}rad ` +
        `${orbit.phi}rad ` +
        `${orbit.radius}m`;
}


// ============================================================
// POINTING
// ============================================================

function handlePointing(data) {

    const x = clamp(
        Number(data.point_x),
        0,
        1
    );

    const y = clamp(
        Number(data.point_y),
        0,
        1
    );


    /*
        We deliberately do NOT change the
        camera target here.

        Pointing is currently a selection/
        cursor gesture rather than camera
        movement.

        This keeps the 3D field stable while
        giving us the hand position for future
        field-object selection.
    */

    let cursor =
        document.getElementById(
            "gestureCursor"
        );


    if (!cursor) {

        cursor =
            document.createElement("div");

        cursor.id =
            "gestureCursor";

        cursor.style.position =
            "absolute";

        cursor.style.width =
            "22px";

        cursor.style.height =
            "22px";

        cursor.style.border =
            "2px solid rgba(255,255,255,0.9)";

        cursor.style.borderRadius =
            "50%";

        cursor.style.transform =
            "translate(-50%, -50%)";

        cursor.style.pointerEvents =
            "none";

        cursor.style.zIndex =
            "20";

        cursor.style.boxShadow =
            "0 0 16px rgba(255,255,255,0.45)";

        document
            .querySelector(".app")
            ?.appendChild(cursor);
    }


    cursor.style.left =
        `${x * 100}%`;

    cursor.style.top =
        `${y * 100}%`;

    cursor.style.display =
        "block";


    updateInfoPanel(true, data.point_info);
}


// ============================================================
// FIELD INFORMATION PANEL
// ============================================================

// Populated from data.point_info while the point gesture is active.
// See config.POINT_INFORMATION (Python side) -- this file never
// hard-codes any field content itself.
function updateInfoPanel(active, info) {

    let panel =
        document.getElementById(
            "infoPanel"
        );


    if (!panel) {

        panel =
            document.createElement("div");

        panel.id =
            "infoPanel";

        panel.className =
            "info-panel hidden";

        panel.innerHTML =
            '<div class="info-title"></div>' +
            '<div class="info-status"></div>' +
            '<div class="info-description"></div>' +
            '<div class="info-details"></div>';

        document
            .querySelector(".app")
            ?.appendChild(panel);
    }


    if (!active) {

        panel.classList.add(
            "hidden"
        );

        return;
    }


    const safeInfo = info || {};

    const title = safeInfo.title || "";
    const description = safeInfo.description || "";
    const status = safeInfo.status || "";
    const details = safeInfo.details || "";

    const hasContent =
        title || description || status || details;


    const titleEl = panel.querySelector(".info-title");
    const statusFieldEl = panel.querySelector(".info-status");
    const descriptionEl = panel.querySelector(".info-description");
    const detailsEl = panel.querySelector(".info-details");

    if (titleEl) {
        titleEl.textContent =
            title || "Field Information";
    }

    if (statusFieldEl) {
        statusFieldEl.textContent = status;
    }

    if (descriptionEl) {
        descriptionEl.textContent = hasContent
            ? description
            : "No field information configured yet.";
    }

    if (detailsEl) {
        detailsEl.textContent = details;
    }


    panel.classList.remove(
        "hidden"
    );
}


// ============================================================
// HIDE POINTER
// ============================================================

function hideGestureCursor() {

    const cursor =
        document.getElementById(
            "gestureCursor"
        );

    if (cursor) {

        cursor.style.display =
            "none";
    }
}


// ============================================================
// GESTURE STATE
// ============================================================

function handleGesture(data) {

    if (!data) {
        return;
    }


    const gesture =
        data.gesture || "none";


    // --------------------------------------------
    // ROTATE
    // --------------------------------------------

    if (gesture === "rotate") {

        handleRotation(data);

    } else {

        lastRotateX = null;
        lastRotateY = null;
    }


    // --------------------------------------------
    // PINCH
    // --------------------------------------------

    if (
        gesture === "pinching" &&
        data.pinch_active
    ) {

        handlePinch(data);

    } else {

        lastPinchDistance = null;
    }


    // --------------------------------------------
    // POINT
    // --------------------------------------------

    if (gesture === "pointing") {

        handlePointing(data);

    } else {

        hideGestureCursor();
        updateInfoPanel(false, null);
    }


    // --------------------------------------------
    // STATUS
    // --------------------------------------------

    if (
        statusEl &&
        gesture !== lastGesture
    ) {

        if (gesture === "rotate") {

            statusEl.textContent =
                "ROTATE • HAND ACTIVE";

        } else if (
            gesture === "pinching"
        ) {

            const direction =
                data.zoom_direction;

            if (direction === "in") {

                statusEl.textContent =
                    "ZOOM IN • PINCH";

            } else if (
                direction === "out"
            ) {

                statusEl.textContent =
                    "ZOOM OUT • PINCH";

            } else {

                statusEl.textContent =
                    "PINCH • READY";
            }

        } else if (
            gesture === "pointing"
        ) {

            statusEl.textContent =
                "POINT • FIELD CURSOR";

        } else {

            statusEl.textContent =
                "MODEL READY • GESTURE CONTROL";
        }
    }


    lastGesture = gesture;
}


// ============================================================
// FETCH GESTURE DATA
// ============================================================

async function pollGesture() {

    try {

        const response =
            await fetch(
                GESTURE_ENDPOINT,
                {
                    cache: "no-store"
                }
            );


        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        handleGesture(data);


    } catch (error) {

        // Do not spam the console.
        const now =
            performance.now();


        if (
            now - lastGestureTimestamp
            > 3000
        ) {

            console.warn(
                "Gesture API unavailable:",
                error
            );

            lastGestureTimestamp =
                now;
        }
    }


    window.setTimeout(
        pollGesture,
        35
    );
}


// ============================================================
// KEYBOARD
// ============================================================

document.addEventListener(
    "keydown",
    (event) => {

        const key =
            event.key.toLowerCase();


        if (key === "r") {

            resetCamera();
        }


        if (
            key === "f" &&
            fullscreenButton
        ) {

            fullscreenButton.click();
        }
    }
);


// ============================================================
// START
// ============================================================

resetCamera();

pollGesture();