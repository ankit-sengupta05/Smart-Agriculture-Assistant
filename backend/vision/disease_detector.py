"""
PlantGuard - Computer Vision Module
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
# Disease Colour Signatures  (all treatment strings kept under 100 chars)
# ---------------------------------------------------------------------------

DISEASE_SIGNATURES = {
    "Leaf Blight": {
        "hsv_lower": np.array([10, 50, 50]),
        "hsv_upper": np.array([25, 255, 200]),
        "color": "#E67E22",
        "treatment": (
            "Apply copper-based fungicide. "
            "Remove and destroy infected leaves. "
            "Ensure adequate spacing for air circulation."
        ),
    },
    "Powdery Mildew": {
        "hsv_lower": np.array([0, 0, 200]),
        "hsv_upper": np.array([180, 30, 255]),
        "color": "#BDC3C7",
        "treatment": (
            "Apply sulfur-based fungicide or neem oil. " "Reduce humidity. Avoid overhead watering."
        ),
    },
    "Rust": {
        "hsv_lower": np.array([5, 100, 100]),
        "hsv_upper": np.array([15, 255, 255]),
        "color": "#E74C3C",
        "treatment": (
            "Apply triazole fungicide at first sign. "
            "Remove infected plant debris. Use resistant varieties."
        ),
    },
    "Mosaic Virus": {
        "hsv_lower": np.array([35, 40, 40]),
        "hsv_upper": np.array([85, 180, 180]),
        "color": "#2ECC71",
        "treatment": (
            "No cure - remove infected plants immediately. "
            "Control aphid vectors with insecticide."
        ),
    },
    "Root Rot": {
        "hsv_lower": np.array([0, 60, 20]),
        "hsv_upper": np.array([15, 180, 80]),
        "color": "#8E44AD",
        "treatment": (
            "Improve drainage. "
            "Apply systemic fungicide (metalaxyl). "
            "Reduce irrigation frequency."
        ),
    },
    "Bacterial Leaf Spot": {
        "hsv_lower": np.array([20, 30, 30]),
        "hsv_upper": np.array([35, 150, 120]),
        "color": "#F39C12",
        "treatment": (
            "Apply copper bactericide. "
            "Avoid working in wet conditions. "
            "Use disease-free seeds."
        ),
    },
}

SEVERITY_THRESHOLDS = {"mild": 5.0, "moderate": 15.0, "severe": 30.0}
TARGET_SIZE = (640, 480)


# ---------------------------------------------------------------------------
# Main Detector Class
# ---------------------------------------------------------------------------


class CropDiseaseDetector:
    """
    Five-stage OpenCV pipeline:
      1. Pre-process  - resize, CLAHE, fast NL-means denoising
      2. Segment      - HSV green-range mask + morphological cleanup
      3. Detect       - per-disease colour threshold + contour analysis
      4. Annotate     - bounding boxes, labels, severity banner
      5. Return       - ScanResult with base64 annotated image
    """

    def __init__(self, model_path: Optional[str] = None):
        self.deep_model = None
        if model_path:
            try:
                self.deep_model = cv2.dnn.readNet(model_path)
                logger.info("DNN model loaded: %s", model_path)
            except Exception as e:
                logger.warning("DNN load failed (%s) - using rule-based detector", e)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan_from_file(self, path: str) -> ScanResult:
        img = cv2.imread(path)
        if img is None:
            raise ValueError("Cannot read image: %s" % path)
        return self._process(img)

    def scan_from_bytes(self, data: bytes) -> ScanResult:
        arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Cannot decode image bytes")
        return self._process(img)

    def scan_from_base64(self, b64: str) -> ScanResult:
        return self.scan_from_bytes(base64.b64decode(b64))

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    def _process(self, img: np.ndarray) -> ScanResult:
        t0 = time.time()

        resized = cv2.resize(img, TARGET_SIZE)
        denoised = cv2.fastNlMeansDenoisingColored(resized, None, 10, 10, 7, 21)
        enhanced = self._clahe(denoised)
        leaf_mask = self._segment_leaf(enhanced)
        diseases = self._detect_diseases(enhanced, leaf_mask)

        annotated = self._annotate(resized.copy(), diseases, leaf_mask)
        _, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
        img_b64 = base64.b64encode(buf).decode()

        leaf_px = int(np.sum(leaf_mask > 0))
        total_px = leaf_mask.shape[0] * leaf_mask.shape[1]
        contours, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        metadata = {
            "image_size": list(TARGET_SIZE),
            "leaf_coverage_pct": round(leaf_px / total_px * 100, 1),
            "contour_count": len(contours),
            "mean_green": round(float(np.mean(enhanced[:, :, 1])), 2),
            "mean_brightness": round(
                float(np.mean(cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY))),
                2,
            ),
        }

        total_affected = sum(d.affected_area_percent for d in diseases)
        severity = self._overall_severity(total_affected)
        ms = round((time.time() - t0) * 1000, 1)

        logger.info(
            "Scan done in %sms - %d disease(s), severity=%s",
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

    # ------------------------------------------------------------------
    # Stage implementations
    # ------------------------------------------------------------------

    def _clahe(self, img: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def _segment_leaf(self, img: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, np.array([25, 30, 30]), np.array([95, 255, 255]))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        flood = mask.copy()
        h, w = flood.shape
        cv2.floodFill(flood, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
        return mask | cv2.bitwise_not(flood)

    def _detect_diseases(self, img: np.ndarray, leaf_mask: np.ndarray) -> List[DetectedDisease]:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        leaf_area = max(1, int(np.sum(leaf_mask > 0)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        diseases = []

        for name, sig in DISEASE_SIGNATURES.items():
            color_mask = cv2.inRange(hsv, sig["hsv_lower"], sig["hsv_upper"])
            disease_mask = cv2.bitwise_and(color_mask, color_mask, mask=leaf_mask)
            disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_OPEN, kernel)

            affected_px = int(np.sum(disease_mask > 0))
            if affected_px < 100:
                continue

            affected_pct = affected_px / leaf_area * 100
            contours, _ = cv2.findContours(disease_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            bboxes = []
            for cnt in contours:
                if cv2.contourArea(cnt) < 200:
                    continue
                x, y, w, h = cv2.boundingRect(cnt)
                conf = float(np.clip(cv2.contourArea(cnt) / 5000, 0.4, 0.98))
                bboxes.append(BoundingBox(x=x, y=y, width=w, height=h, confidence=conf))

            if not bboxes:
                continue

            sev = "mild"
            if affected_pct > SEVERITY_THRESHOLDS["severe"]:
                sev = "severe"
            elif affected_pct > SEVERITY_THRESHOLDS["moderate"]:
                sev = "moderate"

            diseases.append(
                DetectedDisease(
                    name=name,
                    confidence=round(float(np.mean([b.confidence for b in bboxes])), 3),
                    severity=sev,
                    bounding_boxes=bboxes[:10],
                    affected_area_percent=round(affected_pct, 2),
                    color=sig["color"],
                    treatment=sig["treatment"],
                )
            )

        return sorted(diseases, key=lambda d: d.affected_area_percent, reverse=True)

    def _annotate(
        self,
        img: np.ndarray,
        diseases: List[DetectedDisease],
        leaf_mask: np.ndarray,
    ) -> np.ndarray:
        overlay = img.copy()
        overlay[leaf_mask > 0] = (overlay[leaf_mask > 0] * 0.7 + np.array([0, 80, 0]) * 0.3).astype(
            np.uint8
        )
        cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)

        for d in diseases:
            hex_c = d.color.lstrip("#")
            bgr = (
                int(hex_c[4:6], 16),
                int(hex_c[2:4], 16),
                int(hex_c[0:2], 16),
            )
            for bb in d.bounding_boxes:
                cv2.rectangle(
                    img,
                    (bb.x, bb.y),
                    (bb.x + bb.width, bb.y + bb.height),
                    bgr,
                    2,
                )
                label = "%s %.0f%%" % (d.name, bb.confidence * 100)
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(
                    img,
                    (bb.x, bb.y - th - 8),
                    (bb.x + tw + 4, bb.y),
                    bgr,
                    -1,
                )
                cv2.putText(
                    img,
                    label,
                    (bb.x + 2, bb.y - 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

        if diseases:
            banner = "DETECTED: %s - %s" % (
                diseases[0].name.upper(),
                diseases[0].severity.upper(),
            )
            bcolor = {
                "mild": (0, 200, 255),
                "moderate": (0, 140, 255),
                "severe": (0, 0, 230),
            }.get(diseases[0].severity, (0, 200, 255))
        else:
            banner = "NO DISEASE DETECTED"
            bcolor = (0, 180, 0)

        cv2.rectangle(img, (0, 0), (img.shape[1], 32), bcolor, -1)
        cv2.putText(
            img,
            banner,
            (10, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return img

    def _overall_severity(self, total_pct: float) -> str:
        if total_pct < SEVERITY_THRESHOLDS["mild"]:
            return "none"
        if total_pct < SEVERITY_THRESHOLDS["moderate"]:
            return "mild"
        if total_pct < SEVERITY_THRESHOLDS["severe"]:
            return "moderate"
        return "severe"

    def _recommendations(self, diseases: List[DetectedDisease], severity: str) -> List[str]:
        if not diseases:
            return ["Crop appears healthy. Continue monitoring weekly."]
        recs = ["%s: %s" % (d.name, d.treatment) for d in diseases[:3]]
        if severity in ("moderate", "severe"):
            recs.append("High disease pressure - consult a local agronomist.")
        if severity == "severe":
            recs.append("Consider quarantining this field to prevent spread.")
        recs.append("Re-scan in 7 days to monitor treatment effectiveness.")
        return recs


# ---------------------------------------------------------------------------
# Convenience wrapper for Flask route /api/scan/disease
# ---------------------------------------------------------------------------


def scan_uploaded_image(image_data: bytes, model_path: Optional[str] = None) -> Dict:
    """Accepts raw image bytes, returns JSON-serialisable dict."""
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
