"""
PlantGuard Backend API
FastAPI server for Yield Prediction and Disease Detection
Compatible with React frontend
"""

import time
from typing import Dict

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ml_pipeline.yield_predictor import predict_yield
from vision.disease_detector import scan_uploaded_image

app = FastAPI(title="PlantGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "PlantGuard API running"}


# -------------------------------------------------------------------
# Yield Prediction Endpoint
# -------------------------------------------------------------------


@app.post("/predict")
async def predict(data: Dict) -> Dict:
    """
    Receives crop parameters and returns predicted yield
    """

    result = predict_yield(data)

    return {
        "predicted_yield_tons": result["predicted_yield_tons"],
        "confidence_score": result["confidence_score"],
        "lower_bound": result["lower_bound"],
        "upper_bound": result["upper_bound"],
        "feature_importance": result["feature_importance"],
        "recommendations": result["recommendations"],
        "model_version": result["model_version"],
    }


# -------------------------------------------------------------------
# Disease Detection Endpoint
# -------------------------------------------------------------------


@app.post("/scan")
async def scan(file: UploadFile = File(...)) -> Dict:
    """
    Upload crop image and detect diseases
    """

    start = time.time()

    contents = await file.read()

    result = scan_uploaded_image(contents)

    result["processing_time_ms"] = round((time.time() - start) * 1000, 2)

    return result
