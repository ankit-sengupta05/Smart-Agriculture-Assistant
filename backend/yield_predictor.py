"""
Smart Agriculture Assistant — ML Pipeline
Crop Yield Prediction using TensorFlow + Pandas
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


@dataclass
class CropFeatures:
    crop_type: str
    area_hectares: float
    planting_date: str
    soil_type: str
    irrigation_type: str
    rainfall_mm: float
    temperature_avg: float
    temperature_min: float
    temperature_max: float
    humidity_percent: float
    solar_radiation: float
    fertilizer_kg_per_ha: float = 0.0
    pesticide_applications: int = 0
    historical_yield_avg: Optional[float] = None


@dataclass
class PredictionResult:
    predicted_yield_tons: float
    confidence_score: float
    lower_bound: float
    upper_bound: float
    feature_importance: Dict[str, float]
    recommendations: List[str]
    model_version: str = "v2.1-tf"


# ---------------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------------

CROP_ENCODING = {
    "wheat": 0,
    "rice": 1,
    "corn": 2,
    "soybean": 3,
    "cotton": 4,
    "sugarcane": 5,
    "tomato": 6,
    "potato": 7,
    "onion": 8,
    "other": 9,
}

SOIL_ENCODING = {
    "clay": 0,
    "loam": 1,
    "sandy": 2,
    "silt": 3,
    "peat": 4,
    "chalky": 5,
    "clay_loam": 6,
}

IRRIGATION_ENCODING = {
    "none": 0,
    "drip": 1,
    "sprinkler": 2,
    "flood": 3,
    "furrow": 4,
}


def engineer_features(features: CropFeatures) -> pd.DataFrame:
    """Convert CropFeatures → ML-ready DataFrame."""
    planting_dt = pd.Timestamp(features.planting_date)

    row = {
        "crop_type_enc": CROP_ENCODING.get(features.crop_type, 9),
        "soil_type_enc": SOIL_ENCODING.get(features.soil_type, 1),
        "irrigation_enc": IRRIGATION_ENCODING.get(
            features.irrigation_type,
            0,
        ),
        "area_hectares": features.area_hectares,
        "planting_month": planting_dt.month,
        "planting_doy": planting_dt.day_of_year,
        "rainfall_mm": features.rainfall_mm,
        "temp_avg": features.temperature_avg,
        "temp_range": features.temperature_max - features.temperature_min,
        "humidity_pct": features.humidity_percent,
        "solar_radiation": features.solar_radiation,
        "gdd": max(0, features.temperature_avg - 10) * 90,
        "aridity_index": features.rainfall_mm
        / (
            0.0023
            * (features.temperature_avg + 17.8)
            * (features.temperature_max - features.temperature_min) ** 0.5
            * 30
            + 1e-6
        ),
        "fertilizer_kg_ha": features.fertilizer_kg_per_ha,
        "pesticide_apps": features.pesticide_applications,
        "hist_yield": features.historical_yield_avg or 0.0,
        "has_history": 1 if features.historical_yield_avg else 0,
    }

    df = pd.DataFrame([row])

    continuous_cols = [
        "area_hectares",
        "rainfall_mm",
        "temp_avg",
        "temp_range",
        "humidity_pct",
        "solar_radiation",
        "gdd",
        "aridity_index",
        "fertilizer_kg_ha",
        "hist_yield",
    ]

    MEANS = {
        "area_hectares": 5.0,
        "rainfall_mm": 600,
        "temp_avg": 22,
        "temp_range": 12,
        "humidity_pct": 65,
        "solar_radiation": 18,
        "gdd": 1080,
        "aridity_index": 1.5,
        "fertilizer_kg_ha": 120,
        "hist_yield": 3.5,
    }

    STDS = {
        "area_hectares": 10.0,
        "rainfall_mm": 300,
        "temp_avg": 8,
        "temp_range": 6,
        "humidity_pct": 20,
        "solar_radiation": 6,
        "gdd": 500,
        "aridity_index": 1.0,
        "fertilizer_kg_ha": 80,
        "hist_yield": 2.0,
    }

    for col in continuous_cols:
        df[f"{col}_norm"] = (df[col] - MEANS[col]) / STDS[col]

    logger.info(
        "Feature engineering complete — %s features for %s",
        df.shape[1],
        features.crop_type,
    )

    return df


# ---------------------------------------------------------------------------
# Predictor
# ---------------------------------------------------------------------------


class YieldPredictor:
    BASELINE_YIELDS = {
        "wheat": 3.2,
        "rice": 4.5,
        "corn": 5.8,
        "soybean": 2.7,
        "cotton": 1.8,
        "sugarcane": 65.0,
        "tomato": 35.0,
        "potato": 22.0,
        "onion": 18.0,
        "other": 3.0,
    }

    def _generate_recommendations(
        self,
        f: CropFeatures,
        predicted_yield: float,
    ) -> List[str]:
        recs = []

        if f.rainfall_mm < 400:
            recs.append(
                "⚠️ Low rainfall detected — consider supplemental "
                "irrigation to prevent water stress."
            )

        if f.fertilizer_kg_per_ha < 80:
            recs.append(
                "🌱 Fertilizer below optimal — increasing nitrogen " "could improve yield by 15-20%."
            )

        if f.irrigation_type == "none" and f.crop_type in ["rice", "sugarcane"]:
            recs.append("💧 Drip or flood irrigation is strongly " "recommended for this crop.")

        if f.temperature_avg > 35:
            recs.append("🌡️ High temperature stress risk — " "consider heat-tolerant varieties.")

        if f.soil_type == "sandy":
            recs.append(
                "🪨 Sandy soil detected — add organic matter " "and increase irrigation frequency."
            )

        if not recs:
            recs.append("✅ Growing conditions look favourable — " "maintain current practices.")

        if predicted_yield > 0:
            recs.append("📊 Expected harvest window: " "85–95 days from planting.")

        return recs
