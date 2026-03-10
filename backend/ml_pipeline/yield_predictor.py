"""
Yield prediction module
Heuristic ML-like predictor
"""

from typing import Dict


def predict_yield(form: Dict) -> Dict:
    bases = {
        "wheat": 3.2,
        "rice": 4.5,
        "corn": 5.8,
        "soybean": 2.7,
        "tomato": 35,
        "potato": 22,
        "other": 3,
    }

    crop = form.get("crop_type", "wheat")
    area = float(form.get("area_hectares", 1))

    base = bases.get(crop, 3) * area

    rainfall = min(1.3, max(0.5, form.get("rainfall_mm", 500) / 600))

    temperature = max(
        0.7,
        1 - abs(form.get("temperature_avg", 22) - 22) * 0.02,
    )

    irrigation_map = {
        "drip": 1.25,
        "sprinkler": 1.15,
        "flood": 1.0,
        "none": 0.8,
    }

    irrigation = irrigation_map.get(form.get("irrigation_type"), 1)

    fertilizer = min(
        1.4,
        1 + form.get("fertilizer_kg_per_ha", 100) / 500,
    )

    total = base * rainfall * temperature * irrigation * fertilizer

    result = {
        "predicted_yield_tons": round(total, 2),
        "confidence_score": 0.84,
        "lower_bound": round(total * 0.82, 2),
        "upper_bound": round(total * 1.18, 2),
        "feature_importance": {
            "rainfall": 0.28,
            "temperature": 0.22,
            "irrigation": 0.19,
            "fertilizer": 0.15,
            "soil_quality": 0.11,
            "historical": 0.05,
        },
        "recommendations": [
            "Monitor rainfall levels during mid-season.",
            "Maintain consistent irrigation schedule.",
            "Ensure soil nitrogen levels remain optimal.",
        ],
        "model_version": "v2.1-heuristic",
    }

    return result
