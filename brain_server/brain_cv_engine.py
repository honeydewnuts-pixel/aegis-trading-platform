"""

Project : AEGIS
Module : brain_cv_engine.py

Purpose

Computer Vision Engine for the AEGIS Indicator Rulebook Brain.

This module loads the standardized vision configuration and extracts
indicator coordinates + cross signals from Mobile MT5 screenshots.

"""

from __future__ import annotations

import json
import os
import glob

import cv2
import numpy as np

# ------------------------------------------------------------------
# Configuration Constants
# ------------------------------------------------------------------

CONFIG_FILENAME = "colors_config.json"
DEFAULT_VALIDATION_FOLDER = "./validation_images"

# ------------------------------------------------------------------
# Configuration Loader - CHUNK 1
# ------------------------------------------------------------------

def load_config(config_path: str | None = None) -> dict:
    """
    Load the AEGIS vision configuration.
    """
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
# Indicator Extraction - CHUNK 2
# ------------------------------------------------------------------

def extract_indicators(image: np.ndarray, config: dict) -> dict:
    """Extract pixel coordinates for all 6 indicators using HSV masking."""
    h, w = image.shape[:2]
    results = {}
    hsv_full = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    for key, indicator in config["indicators"].items():
        rgb = np.array(indicator["rgb"], dtype=np.uint8)
        tolerance = indicator["tolerance"]

        # Convert RGB to HSV
        hsv_color = cv2.cvtColor(np.array([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]

        # Build bounds with tolerance
        lower = np.array([max(0, int(hsv_color[0])-tolerance), 50, 50])
        upper = np.array([min(180, int(hsv_color[0])+tolerance), 255, 255])

        # Mask and contours
        mask = cv2.inRange(hsv_full, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        points = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 12: # from noise_filter
                M = cv2.moments(cnt)
                if M["m00"]!= 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    points.append([cx, cy])

        # Sort by x for candle order
        results[key] = sorted(points, key=lambda p: p[0])

    return results

# ------------------------------------------------------------------
# Cross Detection - CHUNK 3
# ------------------------------------------------------------------

def detect_cross(data: dict, config: dict) -> dict:
    """Detect #2 vs #1 cross signals."""
    signals_found = []
    signals_config = config["cross_detection"]["signals"]

    bands2 = data.get("#2", [])
    bands1 = data.get("#1", [])

    if len(bands2) < 2 or len(bands1) < 3:
        return {"cross_detected": False, "signals": []}

    # Simplified: check last 2 points of #2 vs avg of #1
    y2_last = bands2[-1][1]
    y2_prev = bands2[-2][1]
    y1_avg = np.mean([p[1] for p in bands1[-5:]]) # middle band proxy

    # #2(2M)_CROSSED_ABOVE_#1(1U) - simplified check
    if y2_prev > y1_avg and y2_last < y1_avg:
        if signals_config[0] in signals_config:
            signals_found.append(signals_config[0])

    #2(2M)_CROSSED_BELOW_#1(1L) - simplified check
    if y2_prev < y1_avg and y2_last > y1_avg:
        if signals_config[1] in signals_config:
            signals_found.append(signals_config[1])

    return {"cross_detected": len(signals_found) > 0, "signals": signals_found}

# ------------------------------------------------------------------
# Batch Processing - CHUNK 4
# ------------------------------------------------------------------

def process_folder(folder_path: str, config: dict) -> dict:
    """Process all images in folder and return JSON results."""
    all_results = {}
    image_paths = sorted(glob.glob(os.path.join(folder_path, "*.png")) +
                         glob.glob(os.path.join(folder_path, "*.jpg")))

    if not image_paths:
        print(f"⚠️ No images found in {folder_path}")
        return {}

    for img_path in image_paths:
        img_name = os.path.basename(img_path)
        image = cv2.imread(img_path)

        if image is None:
            continue

        extracted = extract_indicators(image, config)
        cross = detect_cross(extracted, config)

        all_results[img_name] = {**extracted, **cross}
        print(f"Processed: {img_name}")

    return all_results

# ------------------------------------------------------------------
# Main - CHUNK 5
# ------------------------------------------------------------------

def main():
    config = load_config()
    results = process_folder(DEFAULT_VALIDATION_FOLDER, config)

    print("\n" + "="*50)
    print("AEGIS EXTRACTION RESULTS")
    print("="*50)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
