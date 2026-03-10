"""
PlantGuard — Computer Vision Module
OpenCV Real-Time Crop Disease Detection
"""

import base64
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


# ── Data Structures ───────────────────────────────────────────────────────────


@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int
    confidence: float


@dataclass
class DetectedDisease:
    name: str
    confidence: float
    severity: str
    bounding_boxes: List[BoundingBox]
    affected_area_percent: float
    color: str
    treatment: str


@dataclass
class ScanResult:
    diseases: List[DetectedDisease]
    overall_severity: str
    total_affected_percent: float
    opencv_metadata: Dict
    processing_time_ms: float
    recommendations: List[str]
    annotated_image_b64: Optional[str] = None


# ── Disease Colour Signatures ─────────────────────────────────────────────────

DISEASE_SIGNATURES = {
    "Leaf Blight": {
        "hsv_lower": np.array([10, 50, 50]),
        "hsv_upper": np.array([25, 255, 200]),
        "color": "#E67E22",
        "treatment": (
            "Apply copper-based fungicide. Remove and destroy infected leaves. "
            "Ensure adequate spacing for air circulation."
        ),
    },
    "Powdery Mildew": {
        "hsv_lower": np.array([0, 0, 200]),
        "hsv_upper": np.array([180, 30, 255]),
        "color": "#BDC3C7",
        "treatment": (
            "Apply sulfur-based fungicide or neem oil. Reduce humidity. " "Avoid overhead watering."
        ),
    },
    "Rust": {
        "hsv_lower": np.array([5, 100, 100]),
        "hsv_upper": np.array([15, 255, 255]),
        "color": "#E74C3C",
        "treatment": (
            "Apply triazole fungicide at first sign. Remove infected plant debris. "
            "Use resistant varieties."
        ),
    },
    "Mosaic Virus": {
        "hsv_lower": np.array([35, 40, 40]),
        "hsv_upper": np.array([85, 180, 180]),
        "color": "#2ECC71",
        "treatment": (
            "No cure — remove infected plants immediately. "
            "Control aphid vectors with insecticide."
        ),
    },
    "Root Rot": {
        "hsv_lower": np.array([0, 60, 20]),
        "hsv_upper": np.array([15, 180, 80]),
        "color": "#8E44AD",
        "treatment": (
            "Improve drainage. Apply systemic fungicide (metalaxyl). "
            "Reduce irrigation frequency."
        ),
    },
    "Bacterial Leaf Spot": {
        "hsv_lower": np.array([20, 30, 30]),
        "hsv_upper": np.array([35, 150, 120]),
        "color": "#F39C12",
        "treatment": (
            "Apply copper bactericide. Avoid working in wet conditions. " "Use disease-free seeds."
        ),
    },
}

SEVERITY_THRESHOLDS = {"mild": 5.0, "moderate": 15.0, "severe": 30.0}
TARGET_SIZE = (640, 480)


# ── Main Detector ─────────────────────────────────────────────────────────────


class CropDiseaseDetector:
    """
    Five-stage OpenCV pipeline:
    1. Pre-process
    2. Segment
    3. Detect
    4. Annotate
    5. Return ScanResult
    """

    def __init__(self, model_path: Optional[str] = None):
        self.deep_model = None
        if model_path:
            try:
                self.deep_model = cv2.dnn.readNet(model_path)
                logger.info("DNN model loaded: %s", model_path)
            except Exception as e:
                logger.warning(
                    "DNN load failed (%s) — using rule-based detector",
                    e,
                )

    # ── Public API ────────────────────────────────────────────────────────────

    def scan_from_file(self, path: str) -> ScanResult:
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Cannot read image: {path}")
        return self._process(img)

    def scan_from_bytes(self, data: bytes) -> ScanResult:
        arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Cannot decode image bytes")
        return self._process(img)

    def scan_from_base64(self, b64: str) -> ScanResult:
        return self.scan_from_bytes(base64.b64decode(b64))

    # ── Pipeline ──────────────────────────────────────────────────────────────

    def _process(self, img: np.ndarray) -> ScanResult:
        t0 = time.time()

        resized = cv2.resize(img, TARGET_SIZE)
        denoised = cv2.fastNlMeansDenoisingColored(resized, None, 10, 10, 7, 21)
        enhanced = self._clahe(denoised)

        leaf_mask = self._segment_leaf(enhanced)

        diseases = self._detect_diseases(enhanced, leaf_mask)

        annotated = self._annotate(resized.copy(), diseases, leaf_mask)

        _, buf = cv2.imencode(
            ".jpg",
            annotated,
            [cv2.IMWRITE_JPEG_QUALITY, 85],
        )
        img_b64 = base64.b64encode(buf).decode()

        leaf_px = int(np.sum(leaf_mask > 0))
        total_px = leaf_mask.shape[0] * leaf_mask.shape[1]

        contours, _ = cv2.findContours(
            leaf_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        metadata = {
            "image_size": list(TARGET_SIZE),
            "leaf_coverage_pct": round(leaf_px / total_px * 100, 1),
            "contour_count": len(contours),
            "mean_green": round(float(np.mean(enhanced[:, :, 1])), 2),
            "mean_brightness": round(
                float(
                    np.mean(
                        cv2.cvtColor(
                            enhanced,
                            cv2.COLOR_BGR2GRAY,
                        )
                    )
                ),
                2,
            ),
        }

        total_affected = sum(d.affected_area_percent for d in diseases)
        severity = self._overall_severity(total_affected)

        ms = round((time.time() - t0) * 1000, 1)

        logger.info(
            "Scan done in %sms — %s disease(s), severity=%s",
            ms,
            len(diseases),
            severity,
        )

        return ScanResult(
            diseases=diseases,
            overall_severity=severity,
            total_affected_percent=round(min(total_affected, 100), 1),
            opencv_metadata=metadata,
            processing_time_ms=ms,
            recommendations=self._recommendations(diseases, severity),
            annotated_image_b64=img_b64,
        )
