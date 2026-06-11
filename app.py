import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import streamlit as st
from PIL import Image
from ultralytics import YOLO


APP_TITLE = "GymMate - Food & Gym Detector"
APP_DESCRIPTION = "Detect food to see calories. Detect gym gear to identify equipment."
MODEL_PATH = Path("models/best.pt")
IMG_SIZE = 640

FOOD_CLASSES = {
    "pizza",
    "burger",
    "ramen",
    "banana",
    "apple",
    "salad",
    "rice",
    "chicken",
}


@st.cache_resource
def load_model(model_path: str = str(MODEL_PATH)) -> YOLO:
    """Load and cache custom YOLOv8 model."""
    model_file = Path(model_path)
    if not model_file.exists():
        raise FileNotFoundError(
            f"Model file not found at '{model_file}'. Put your custom best.pt there."
        )
    return YOLO(model_path)


@st.cache_data
def load_lookup_data() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Load calorie and equipment lookup data."""
    with open("data/nutrition_db.json", "r", encoding="utf-8") as f:
        nutrition_db = json.load(f)
    with open("data/equipment_db.json", "r", encoding="utf-8") as f:
        equipment_db = json.load(f)
    return nutrition_db, equipment_db


def preprocess_image(image: Image.Image, size: int = IMG_SIZE) -> Tuple[np.ndarray, np.ndarray]:
    """Convert PIL image to RGB/BGR numpy arrays and resize for faster inference."""
    rgb = np.array(image.convert("RGB"))
    resized_rgb = cv2.resize(rgb, (size, size), interpolation=cv2.INTER_AREA)
    resized_bgr = cv2.cvtColor(resized_rgb, cv2.COLOR_RGB2BGR)
    return resized_rgb, resized_bgr


def run_detection(model: YOLO, image_bgr: np.ndarray):
    """Run YOLOv8 inference on CPU."""
    results = model.predict(source=image_bgr, imgsz=IMG_SIZE, device="cpu", verbose=False)
    return results[0]


def lookup_calories(item_name: str, nutrition_db: Dict[str, Any]) -> Optional[str]:
    """Return calorie estimate for a detected food item."""
    entry = nutrition_db.get(item_name.lower())
    if not entry:
        return None
    return entry.get("calories_per_serving")


def lookup_equipment(item_name: str, equipment_db: Dict[str, Any]) -> Optional[str]:
    """Return equipment description for a detected gym item."""
    entry = equipment_db.get(item_name.lower())
    if not entry:
        return None
    return entry.get("description")


def draw_boxes(image_rgb: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
    """Draw bounding boxes and labels on image."""
    output = image_rgb.copy()
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = f"{det['label']} ({det['confidence']:.2f})"
        color = (0, 180, 0) if det["type"] == "food" else (220, 70, 70)

        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
        cv2.rectangle(output, (x1, max(y1 - 24, 0)), (x1 + 220, y1), color, -1)
        cv2.putText(
            output,
            label,
            (x1 + 4, max(y1 - 7, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
    return output


def parse_detections(
    result: Any, nutrition_db: Dict[str, Any], equipment_db: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Convert YOLO output to app-friendly detection dictionaries."""
    detections: List[Dict[str, Any]] = []
    names = result.names
    for box in result.boxes:
        cls_id = int(box.cls[0].item())
        label = str(names[cls_id]).lower()
        confidence = float(box.conf[0].item())
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        item_type = "food" if label in FOOD_CLASSES else "gym"
        detection: Dict[str, Any] = {
            "label": label,
            "confidence": confidence,
            "bbox": (x1, y1, x2, y2),
            "type": item_type,
            "calories": None,
            "equipment_info": None,
        }

        if item_type == "food":
            detection["calories"] = lookup_calories(label, nutrition_db)
        else:
            detection["equipment_info"] = lookup_equipment(label, equipment_db)

        detections.append(detection)
    return detections


def display_results(detections: List[Dict[str, Any]]) -> None:
    """Render detection metadata and summary stats."""
    st.subheader("Detected Items")

    if not detections:
        st.info("No objects detected.")
        return

    food_count = sum(1 for d in detections if d["type"] == "food")
    gym_count = sum(1 for d in detections if d["type"] == "gym")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Objects", len(detections))
    col2.metric("Food Items", food_count)
    col3.metric("Gym Equipment", gym_count)

    for i, det in enumerate(detections, start=1):
        line = f"{i}. **{det['label']}** - confidence: `{det['confidence']:.2f}`"
        if det["type"] == "food":
            calories = det["calories"] or "Not found in nutrition DB"
            st.markdown(f"{line} | calories: **{calories}**")
        else:
            equipment_info = det["equipment_info"] or "No description available"
            st.markdown(f"{line} | use: {equipment_info}")


def get_input_image() -> Optional[Image.Image]:
    """Read image from camera input or uploader."""
    st.subheader("Input")
    source = st.radio("Choose image source", ["Camera", "Upload"], horizontal=True)

    if source == "Camera":
        camera_file = st.camera_input("Take a photo")
        if camera_file:
            return Image.open(camera_file)
        return None

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        return Image.open(uploaded_file)
    return None


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_DESCRIPTION)

    st.markdown(
        "Supports custom YOLOv8 classes for food and gym equipment. "
        "Run inference on CPU and view calories/equipment details."
    )

    image = get_input_image()
    detect_clicked = st.button("Detect", type="primary", disabled=image is None)

    if detect_clicked and image is not None:
        try:
            model = load_model()
            nutrition_db, equipment_db = load_lookup_data()
        except Exception as exc:
            st.error(f"Setup error: {exc}")
            st.stop()

        image_rgb, image_bgr = preprocess_image(image, size=IMG_SIZE)
        result = run_detection(model, image_bgr)
        detections = parse_detections(result, nutrition_db, equipment_db)
        annotated = draw_boxes(image_rgb, detections)

        st.subheader("Detection Result")
        st.image(annotated, channels="RGB", use_container_width=True)
        display_results(detections)

    st.divider()
    st.markdown(
        "Tip: place your trained YOLOv8 model at `models/best.pt`. "
        "Class names in your model should match keys in `data/nutrition_db.json` "
        "and `data/equipment_db.json`."
    )


if __name__ == "__main__":
    main()
