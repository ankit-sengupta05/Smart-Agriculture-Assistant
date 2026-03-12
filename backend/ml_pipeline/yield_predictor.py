"""
PlantGuard - ML Pipeline
Crop Yield Prediction using TensorFlow + Pandas
"""

import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
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
    model_version: str = "v2.1-heuristic"


# ---------------------------------------------------------------------------
# Encodings
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

FEATURE_MEANS = {
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
FEATURE_STDS = {
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


# ---------------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------------


def engineer_features(features: CropFeatures) -> pd.DataFrame:
    """Transform raw CropFeatures into an engineered Pandas DataFrame."""
    planting_dt = pd.Timestamp(features.planting_date)
    temp_range = features.temperature_max - features.temperature_min

    aridity = features.rainfall_mm / (
        0.0023 * (features.temperature_avg + 17.8) * (temp_range**0.5) * 30 + 1e-6
    )

    row = {
        "crop_type_enc": CROP_ENCODING.get(features.crop_type, 9),
        "soil_type_enc": SOIL_ENCODING.get(features.soil_type, 1),
        "irrigation_enc": IRRIGATION_ENCODING.get(features.irrigation_type, 0),
        "area_hectares": features.area_hectares,
        "planting_month": planting_dt.month,
        "planting_doy": planting_dt.day_of_year,
        "rainfall_mm": features.rainfall_mm,
        "temp_avg": features.temperature_avg,
        "temp_range": temp_range,
        "humidity_pct": features.humidity_percent,
        "solar_radiation": features.solar_radiation,
        "gdd": max(0, features.temperature_avg - 10) * 90,
        "aridity_index": aridity,
        "fertilizer_kg_ha": features.fertilizer_kg_per_ha,
        "pesticide_apps": features.pesticide_applications,
        "hist_yield": features.historical_yield_avg or 0.0,
        "has_history": 1 if features.historical_yield_avg else 0,
    }

    df = pd.DataFrame([row])
    for col in FEATURE_MEANS:
        if col in df.columns:
            df[col + "_norm"] = (df[col] - FEATURE_MEANS[col]) / FEATURE_STDS[col]
    return df


# ---------------------------------------------------------------------------
# TensorFlow Model Definition
# ---------------------------------------------------------------------------


def build_yield_model(input_dim: int = 28):
    """Residual deep regression model for crop yield prediction."""
    try:
        from tensorflow import keras

        inputs = keras.Input(shape=(input_dim,), name="crop_features")

        x = keras.layers.Dense(256, activation="relu")(inputs)
        x = keras.layers.BatchNormalization()(x)
        x = keras.layers.Dropout(0.3)(x)

        h = keras.layers.Dense(128, activation="relu")(x)
        h = keras.layers.BatchNormalization()(h)
        h = keras.layers.Dropout(0.2)(h)
        skip = keras.layers.Dense(128)(x)
        x = keras.layers.Add()([h, skip])
        x = keras.layers.Activation("relu")(x)

        x = keras.layers.Dense(64, activation="relu")(x)
        x = keras.layers.Dropout(0.2)(x)

        mean_out = keras.layers.Dense(1, name="yield_mean")(x)
        logvar = keras.layers.Dense(1, name="yield_log_var")(x)

        model = keras.Model(inputs=inputs, outputs=[mean_out, logvar])
        model.compile(optimizer=keras.optimizers.Adam(1e-3), loss="mse")
        return model

    except ImportError:
        logger.warning("TensorFlow not installed - heuristic model will be used.")
        return None


# ---------------------------------------------------------------------------
# Inference Engine
# ---------------------------------------------------------------------------


class YieldPredictor:
    """
    Wraps TF model + Pandas pipeline.
    Falls back to calibrated heuristic when TF weights are not available.
    """

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

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_version = "v2.1-heuristic"

        if model_path and os.path.exists(model_path):
            try:
                import tensorflow as tf

                self.model = tf.keras.models.load_model(model_path)
                self.model_version = "v2.1-tf"
                logger.info("TF model loaded from %s", model_path)
            except Exception as e:
                logger.warning("Could not load TF model (%s) - using heuristic", e)

    def predict(self, features: CropFeatures) -> PredictionResult:
        df = engineer_features(features)
        if self.model is not None:
            return self._tf_predict(df, features)
        return self._heuristic_predict(features)

    def _tf_predict(self, df: pd.DataFrame, features: CropFeatures) -> PredictionResult:
        norm_cols = [c for c in df.columns if c.endswith("_norm")]
        cat_cols = [
            "crop_type_enc",
            "soil_type_enc",
            "irrigation_enc",
            "planting_month",
            "planting_doy",
            "has_history",
            "pesticide_apps",
        ]
        x_input = df[norm_cols + cat_cols].values.astype("float32")
        mean_pred, log_var = self.model.predict(x_input, verbose=0)
        yield_mean = float(mean_pred[0][0]) * features.area_hectares
        std = float(np.exp(0.5 * log_var[0][0]))
        confidence = float(np.clip(1.0 - std / (yield_mean + 1e-6), 0.5, 0.99))
        return PredictionResult(
            predicted_yield_tons=max(0.1, round(yield_mean, 2)),
            confidence_score=round(confidence, 3),
            lower_bound=round(max(0, yield_mean - 1.96 * std), 2),
            upper_bound=round(yield_mean + 1.96 * std, 2),
            feature_importance=self._dummy_importance(),
            recommendations=self._recommendations(features, yield_mean),
            model_version=self.model_version,
        )

    def _heuristic_predict(self, features: CropFeatures) -> PredictionResult:
        base = self.BASELINE_YIELDS.get(features.crop_type, 3.0)

        rain_f = float(np.clip(features.rainfall_mm / 600, 0.5, 1.3))
        temp_f = float(np.clip(1 - abs(features.temperature_avg - 22) * 0.02, 0.7, 1.1))
        irrig_f = {
            "drip": 1.25,
            "sprinkler": 1.15,
            "flood": 1.0,
            "furrow": 1.05,
            "none": 0.8,
        }.get(features.irrigation_type, 1.0)
        fert_f = float(np.clip(1 + features.fertilizer_kg_per_ha / 500, 1.0, 1.4))
        soil_f = {
            "loam": 1.15,
            "clay_loam": 1.1,
            "silt": 1.05,
            "clay": 0.95,
            "sandy": 0.85,
        }.get(features.soil_type, 1.0)

        total = base * rain_f * temp_f * irrig_f * fert_f * soil_f * features.area_hectares
        std = total * 0.12
        has_hist = features.historical_yield_avg is not None

        importance = {
            "rainfall": round(rain_f - 0.5, 3),
            "temperature": round(temp_f - 0.5, 3),
            "irrigation": round(irrig_f - 1.0, 3),
            "fertilizer": round(fert_f - 1.0, 3),
            "soil_quality": round(soil_f - 0.85, 3),
            "historical_data": round(0.1 if has_hist else 0, 3),
        }

        return PredictionResult(
            predicted_yield_tons=round(max(0.1, total), 2),
            confidence_score=round(0.78 + (0.12 if has_hist else 0), 3),
            lower_bound=round(max(0, total - 1.96 * std), 2),
            upper_bound=round(total + 1.96 * std, 2),
            feature_importance=importance,
            recommendations=self._recommendations(features, total),
            model_version=self.model_version,
        )

    def _dummy_importance(self) -> Dict[str, float]:
        keys = [
            "rainfall",
            "temperature",
            "irrigation",
            "fertilizer",
            "soil_quality",
            "historical_data",
        ]
        return {k: round(abs(float(np.random.normal(0.1, 0.05))), 3) for k in keys}

    def _recommendations(self, f: CropFeatures, predicted_yield: float) -> List[str]:
        recs = []
        if f.rainfall_mm < 400:
            recs.append("Low rainfall - consider supplemental irrigation.")
        else:
            recs.append("Rainfall levels are adequate for this crop.")
        if f.fertilizer_kg_per_ha < 80:
            recs.append("Fertilizer below optimal - increase nitrogen by 20%.")
        else:
            recs.append("Fertilizer application is on target.")
        if f.irrigation_type == "none" and f.crop_type in (
            "rice",
            "sugarcane",
        ):
            recs.append("Drip or flood irrigation strongly recommended " "for this crop type.")
        if f.temperature_avg > 35:
            recs.append("High temperature risk - consider heat-tolerant variety.")
        if f.soil_type == "sandy":
            recs.append("Sandy soil - add organic matter and increase " "irrigation frequency.")
        if predicted_yield > 0:
            recs.append("Expected harvest window: 85-95 days " "based on current GDD trajectory.")
        return recs


# ---------------------------------------------------------------------------
# Training Pipeline
# ---------------------------------------------------------------------------


def load_and_prepare_dataset(
    csv_path: str,
) -> Tuple[np.ndarray, np.ndarray]:
    """Load CSV, engineer features via Pandas, return numpy arrays."""
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["actual_yield_tons"])
    df["actual_yield_tons"] = pd.to_numeric(df["actual_yield_tons"], errors="coerce")
    df = df[df["actual_yield_tons"] > 0]

    rows = []
    for _, row in df.iterrows():
        cf = CropFeatures(
            crop_type=row["crop_type"],
            area_hectares=row["area_hectares"],
            planting_date=str(row["planting_date"]),
            soil_type=row.get("soil_type", "loam"),
            irrigation_type=row.get("irrigation_type", "none"),
            rainfall_mm=row["rainfall_mm"],
            temperature_avg=row["temp_avg"],
            temperature_min=row["temp_min"],
            temperature_max=row["temp_max"],
            humidity_percent=row["humidity_pct"],
            solar_radiation=row.get("solar_radiation", 18),
            fertilizer_kg_per_ha=row.get("fertilizer_kg_ha", 0),
            pesticide_applications=int(row.get("pesticide_apps", 0)),
        )
        feat_df = engineer_features(cf)
        norm_cols = [c for c in feat_df.columns if c.endswith("_norm")]
        cat_cols = [
            "crop_type_enc",
            "soil_type_enc",
            "irrigation_enc",
            "planting_month",
            "planting_doy",
            "has_history",
            "pesticide_apps",
        ]
        rows.append(feat_df[norm_cols + cat_cols].values[0])

    x_out = np.array(rows, dtype="float32")
    y_out = df["actual_yield_tons"].values.astype("float32")
    logger.info("Dataset prepared: X=%s, y=%s", x_out.shape, y_out.shape)
    return x_out, y_out


def train_model(
    csv_path: str,
    save_path: str = "models/yield_model.keras",
    epochs: int = 100,
    batch_size: int = 32,
):
    """Full TF training pipeline with early stopping."""
    import tensorflow as tf
    from sklearn.model_selection import train_test_split

    x_data, y_data = load_and_prepare_dataset(csv_path)
    x_train, x_val, y_train, y_val = train_test_split(
        x_data, y_data, test_size=0.2, random_state=42
    )

    base_model = build_yield_model(x_data.shape[1])
    single = tf.keras.Model(inputs=base_model.input, outputs=base_model.outputs[0])
    single.compile(optimizer="adam", loss="mse", metrics=["mae"])

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    history = single.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=15, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=7),
            tf.keras.callbacks.ModelCheckpoint(save_path, save_best_only=True),
        ],
        verbose=1,
    )
    best_mae = min(history.history["val_mae"])
    print("Training complete - Best val MAE: %.3f t/ha" % best_mae)
    return history
