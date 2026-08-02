"""
Project : AEGIS
Module : brain_cv_engine.py
Purpose: CV Brain + Cloud API for AEGIS
"""

from __future__ import annotations
import json, os, glob
import cv2
import numpy as np
from flask import Flask, request, jsonify

# ------------------------------------------------------------------
# CHUNK 1: CONFIG LOADER
# ------------------------------------------------------------------
CONFIG_FILENAME = "colors_config.json"
DEFAULT_VALIDATION_FOLDER = "./validation_images"

def load_config(config_path: str | None = None) -> dict:
    if config_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, CONFIG_FILENAME)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r") as f:
        config = json.load(f)
    print(f"✅ Config loaded: {config['config_version']}")
    return config

# ------------------------------------------------------------------
# CHUNK 2: INDICATOR EXTRACTION
# ------------------------------------------------------------------
def extract_indicators(image: np.ndarray, config: dict) -> dict:
    h, w = image.shape[:2]
    results = {}
    hsv_full = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    for key, indicator in config["indicators"].items():
        rgb = np.array(indicator["rgb"], dtype=np.uint8)
        tolerance = indicator["tolerance"]
        hsv_color = cv2.cvtColor(np.array([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
        lower = np.array([max(0, int(hsv_color[0])-tolerance), 50, 50])
        upper = np.array([min(180, int(hsv_color[0])+tolerance), 255, 255])
        mask = cv2.inRange(hsv_full, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        points = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 12:
                M = cv2.moments(cnt)
                if M["m00"]!= 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    points.append([cx, cy])
        results[key] = sorted(points, key=lambda p: p[0])
    return results

# ------------------------------------------------------------------
# CHUNK 3: CROSS DETECTION
# ------------------------------------------------------------------
def detect_cross(data: dict, config: dict) -> dict:
    signals_found = []
    signals_config = config["cross_detection"]["signals"]
    bands2 = data.get("#2", [])
    bands1 = data.get("#1", [])
    if len(bands2) < 2 or len(bands1) < 3:
        return {"cross_detected": False, "signals": []}
    y2_last = bands2[-1][1]
    y2_prev = bands2[-2][1]
    y1_avg = np.mean([p[1] for p in bands1[-5:]])
    if y2_prev > y1_avg and y2_last < y1_avg:
        signals_found.append(signals_config[0])
    if y2_prev < y1_avg and y2_last > y1_avg:
        signals_found.append(signals_config[1])
    return {"cross_detected": len(signals_found) > 0, "signals": signals_found}

# ------------------------------------------------------------------
# CHUNK 4: BATCH PROCESSING
# ------------------------------------------------------------------
def process_folder(folder_path: str, config: dict) -> dict:
    all_results = {}
    image_paths = sorted(glob.glob(os.path.join(folder_path, "*.png")) + glob.glob(os.path.join(folder_path, "*.jpg")))
    if not image_paths:
        print(f"⚠️ No images found in {folder_path}")
        return {}
    for img_path in image_paths:
        img_name = os.path.basename(img_path)
        image = cv2.imread(img_path)
        if image is None: continue
        extracted = extract_indicators(image, config)
        cross = detect_cross(extracted, config)
        all_results[img_name] = {**extracted, **cross}
        print(f"Processed: {img_name}")
    return all_results

# ------------------------------------------------------------------
# CHUNK 5: MAIN TEST RUNNER
# ------------------------------------------------------------------
def main():
    config = load_config()
    results = process_folder(DEFAULT_VALIDATION_FOLDER, config)
    print("\n" + "="*50)
    print("AEGIS EXTRACTION RESULTS")
    print("="*50)
    print(json.dumps(results, indent=2))

# ------------------------------------------------------------------
# CHUNK 6: CLOUD API + FLASK SERVER
# ------------------------------------------------------------------
def analyze_image(image_bytes: bytes) -> dict:
    """Takes screenshot bytes from phone, returns BUY/SELL/HOLD"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        return {"error": "Invalid image"}
    config = load_config()
    extracted = extract_indicators(image, config)
    cross = detect_cross(extracted, config)
    signal = "HOLD"
    if cross["cross_detected"]:
        if "#2(2M)_CROSSED_ABOVE_#1(1U)" in cross["signals"]:
            signal = "BUY"
        elif "#2(2M)_CROSSED_BELOW_#1(1L)" in cross["signals"]:
            signal = "SELL"
    return {"signal": signal, "confidence": 0.95, "details": cross}

app = Flask(__name__)

@app.route("/aegis/analyze", methods=["POST"])
def analyze_endpoint():
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400
    file = request.files['image']
    img_bytes = file.read()
    result = analyze_image(img_bytes)
    return jsonify(result)

if __name__ == "__main__":
    # To run as Cloud Brain API:
    app.run(host="0.0.0.0", port=5000, debug=True)
    # To run local folder test instead, comment line above and uncomment:
    # main()
