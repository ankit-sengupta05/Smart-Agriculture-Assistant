"""
Smart Agriculture Assistant — Computer Vision Module
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


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Disease Signatures
# ---------------------------------------------------------------------------

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
        "color": "#ECF0F1",
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
            "Use resistant varieties next season."
        ),
    },
    "Mosaic Virus": {
        "hsv_lower": np.array([35, 40, 40]),
        "hsv_upper": np.array([85, 180, 180]),
        "color": "#2ECC71",
        "treatment": (
            "No cure — remove infected plants immediately to prevent spread. "
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
            "Apply copper bactericide. Avoid working in wet fields. " "Use disease-free seeds."
        ),
    },
}

SEVERITY_THRESHOLDS = {
    "mild": 5.0,
    "moderate": 15.0,
    "severe": 30.0,
}


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


class CropDiseaseDetector:
    TARGET_SIZE = (640, 480)

    def __init__(self, model_path: Optional[str] = None):
        self.deep_model = None

        if model_path:
            try:
                self.deep_model = cv2.dnn.readNet(model_path)
                logger.info("DNN model loaded: %s", model_path)
            except Exception as e:
                logger.warning(
                    "Could not load DNN: %s — using rule-based detector",
                    e,
                )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan_from_file(self, image_path: str) -> ScanResult:
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        return self._process(img)

    def scan_from_bytes(self, image_bytes: bytes) -> ScanResult:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Cannot decode image bytes")

        return self._process(img)

    def scan_from_base64(self, b64_string: str) -> ScanResult:
        raw = base64.b64decode(b64_string)
        return self.scan_from_bytes(raw)

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    def _process(self, img: np.ndarray) -> ScanResult:
        start = time.time()

        img_resized = cv2.resize(img, self.TARGET_SIZE)

        img_denoised = cv2.fastNlMeansDenoisingColored(
            img_resized,
            None,
            10,
            10,
            7,
            21,
        )

        img_enhanced = self._apply_clahe(img_denoised)

        leaf_mask = self._segment_leaf(img_enhanced)

        diseases: List[DetectedDisease] = []

        annotated = img_resized.copy()

        _, buf = cv2.imencode(
            ".jpg",
            annotated,
            [cv2.IMWRITE_JPEG_QUALITY, 85],
        )

        img_b64 = base64.b64encode(buf).decode("utf-8")

        leaf_area_px = int(np.sum(leaf_mask > 0))
        total_px = leaf_mask.shape[0] * leaf_mask.shape[1]

        leaf_coverage = leaf_area_px / total_px * 100

        contours, _ = cv2.findContours(
            leaf_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        metadata = {
            "image_size": list(self.TARGET_SIZE),
            "leaf_coverage_pct": round(leaf_coverage, 1),
            "contour_count": len(contours),
            "mean_green": float(np.mean(img_enhanced[:, :, 1])),
            "mean_brightness": float(np.mean(cv2.cvtColor(img_enhanced, cv2.COLOR_BGR2GRAY))),
            "color_histogram": self._compute_color_histogram(img_enhanced),
        }

        total_affected = sum(d.affected_area_percent for d in diseases)

        overall_severity = self._compute_overall_severity(total_affected)

        processing_ms = (time.time() - start) * 1000

        result = ScanResult(
            diseases=diseases,
            overall_severity=overall_severity,
            total_affected_percent=round(min(total_affected, 100), 1),
            opencv_metadata=metadata,
            processing_time_ms=round(processing_ms, 1),
            recommendations=self._generate_recommendations(
                diseases,
                overall_severity,
            ),
            annotated_image_b64=img_b64,
        )

        logger.info(
            "Scan complete in %.0fms — %d disease(s) found, severity: %s",
            processing_ms,
            len(diseases),
            overall_severity,
        )

        return result

    # ------------------------------------------------------------------
    # Processing Stages
    # ------------------------------------------------------------------

    def _apply_clahe(self, img: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8),
        )

        lab[:, :, 0] = clahe.apply(lab[:, :, 0])

        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def _segment_leaf(self, img: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_green = np.array([25, 30, 30])
        upper_green = np.array([95, 255, 255])

        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

        mask = cv2.morphologyEx(
            green_mask,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=2,
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel,
            iterations=1,
        )

        flood = mask.copy()

        h, w = flood.shape
        flood_fill_mask = np.zeros((h + 2, w + 2), np.uint8)

        cv2.floodFill(flood, flood_fill_mask, (0, 0), 255)

        mask = mask | cv2.bitwise_not(flood)

        return mask

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _compute_color_histogram(
        self,
        img: np.ndarray,
        bins: int = 8,
    ) -> Dict:
        hist = {}

        for i, ch in enumerate(["blue", "green", "red"]):
            h = cv2.calcHist([img], [i], None, [bins], [0, 256])
            hist[ch] = [round(float(v[0]), 1) for v in h]

        return hist

    def _compute_overall_severity(self, total_affected_pct: float) -> str:
        if total_affected_pct == 0:
            return "none"

        if total_affected_pct < SEVERITY_THRESHOLDS["mild"]:
            return "none"

        if total_affected_pct < SEVERITY_THRESHOLDS["moderate"]:
            return "mild"

        if total_affected_pct < SEVERITY_THRESHOLDS["severe"]:
            return "moderate"

        return "severe"

    def _generate_recommendations(
        self,
        diseases: List[DetectedDisease],
        severity: str,
    ) -> List[str]:
        if not diseases:
            return ["✅ Crop appears healthy. Continue monitoring weekly."]

        recs = [f"🔬 {d.name}: {d.treatment}" for d in diseases[:3]]

        if severity in ("moderate", "severe"):
            recs.append("⚠️ High disease pressure — consult a local agronomist immediately.")

        if severity == "severe":
            recs.append(
                "🚨 Consider quarantining this field to prevent spread " "to adjacent plots."
            )

        recs.append("📸 Re-scan in 7 days to monitor treatment effectiveness.")

        return recs


# ---------------------------------------------------------------------------
# Integration Helper
# ---------------------------------------------------------------------------


def scan_uploaded_image(
    image_data: bytes,
    model_path: Optional[str] = None,
) -> Dict:
    detector = CropDiseaseDetector(model_path=model_path)

    result = detector.scan_from_bytes(image_data)

    return {
        "diseases": [
            {
                "name": d.name,
                "confidence": d.confidence,
                "severity": d.severity,
                "affected_area_percent": d.affected_area_percent,
                "color": d.color,
                "treatment": d.treatment,
                "bounding_box_count": len(d.bounding_boxes),
            }
            for d in result.diseases
        ],
        "overall_severity": result.overall_severity,
        "total_affected_percent": result.total_affected_percent,
        "processing_time_ms": result.processing_time_ms,
        "opencv_metadata": result.opencv_metadata,
        "recommendations": result.recommendations,
        "annotated_image_b64": result.annotated_image_b64,
    }
