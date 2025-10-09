# ==== backend/routers/anomaly.py ====
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict
import random
from datetime import date, timedelta
import numpy as np
from pyod.models.iforest import IForest # Isolation Forest
import pandas as pd # For data manipulation
import os

from ..utils.logger import setup_logging
from ..dependencies import get_current_user, require_roles
from ..schemas.auth import UserRole

router = APIRouter()
logger = setup_logging()

class AnomalyDetectionResponse(BaseModel):
    anomalies: List[Dict]
    model_used: str

# --- MOCK Anomaly Detection Model Setup ---
# This would typically be a trained model loaded at startup.
# We'll train a simple one on synthetic data for demonstration.

# Generate synthetic daily ticket volume data
def generate_synthetic_data(num_days: int = 90):
    """Generates synthetic daily ticket volumes with occasional spikes."""
    data = []
    base_volume = 50
    start_date = date.today() - timedelta(days=num_days - 1)

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        # Normal fluctuation
        volume = base_volume + random.randint(-10, 15)
        
        # Introduce occasional anomalies (spikes)
        if random.random() < 0.05: # 5% chance of an anomaly
            volume += random.randint(30, 80) # Significant spike
            if random.random() < 0.3: # Chance of making it a specific category issue
                category = random.choice(["Network Problem", "Security Incident"])
            else:
                category = "General Anomaly"
        else:
            category = random.choice(["Software Issue", "Hardware Failure", "Account Management"])

        data.append({
            "date": current_date.isoformat(),
            "volume": volume,
            "category_hint": category # For mock anomaly detection
        })
    return pd.DataFrame(data)

# Global variables for the model
isolation_forest_model = None
synthetic_df = None

def train_anomaly_model():
    """Trains the Isolation Forest model on synthetic data."""
    global isolation_forest_model, synthetic_df
    logger.info("Generating synthetic data and training Isolation Forest model...")
    synthetic_df = generate_synthetic_data(num_days=120)
    
    # Isolation Forest expects numerical features. We'll use 'volume'.
    X = synthetic_df[['volume']].values
    
    # Train Isolation Forest
    # contamination: proportion of outliers in the data set (estimate)
    isolation_forest_model = IForest(contamination=0.05, random_state=42)
    isolation_forest_model.fit(X)
    logger.info("Isolation Forest model trained.")

# Train the model on startup
if os.getenv("SKIP_AI_INIT", "false").lower() != "true":
    train_anomaly_model()
else:
    logger.warning("Skipping AI model initialization due to SKIP_AI_INIT=true.")


@router.get("/detect_anomalies", response_model=AnomalyDetectionResponse,
             summary="Detect anomalies in daily ticket volumes",
             response_description="A list of detected anomaly dates and their potential categories.",
             dependencies=[Depends(require_roles([UserRole.ADMIN]))])
async def detect_anomalies(
    current_user: dict = Depends(get_current_user)
):
    """
    Detects unusual patterns or spikes in daily ticket volumes using Isolation Forest.
    Returns a list of dates where anomalies were detected.
    Requires 'Admin' role.
    """
    logger.info(f"Admin user {current_user['email']} requested anomaly detection.")

    if isolation_forest_model is None or synthetic_df is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Anomaly detection service is not initialized. Please check backend logs."
        )

    # Use the trained model to predict anomalies on the synthetic data
    # (In a real app, this would be new incoming data)
    X_test = synthetic_df[['volume']].values
    
    # Get anomaly scores and predictions (-1 for outlier, 1 for inlier)
    y_pred = isolation_forest_model.predict(X_test)
    
    anomalies_list = []
    # Iterate through the predictions and identify outliers
    for i, pred_label in enumerate(y_pred):
        if pred_label == -1: # -1 indicates an outlier/anomaly
            anomaly_data = synthetic_df.iloc[i]
            anomalies_list.append({
                "date": anomaly_data["date"],
                "volume": int(anomaly_data["volume"]),
                "category_hint": anomaly_data["category_hint"],
                "reason": "Unusual spike in ticket volume detected."
            })
    
    logger.info(f"Detected {len(anomalies_list)} anomalies.")
    return AnomalyDetectionResponse(
        anomalies=anomalies_list,
        model_used="Isolation Forest (PyOD)"
    )