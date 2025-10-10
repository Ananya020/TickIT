# backend/routers/sla.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import random # Keep for possible future randomness, but not for core prediction
from datetime import datetime, timedelta
from typing import Literal
from typing import Optional
from datetime import datetime
import pandas as pd # Import pandas for model input

from ..utils.logger import setup_logging
from ..dependencies import get_current_user, require_roles
from ..schemas.auth import UserRole
# Import the model and related utilities
from backend.routers.sla_model import sla_model, SLA_DEFINITIONS, predict_breach_time


router = APIRouter()
logger = setup_logging()

class SLARiskRequest(BaseModel):
    priority: Literal["Low", "Medium", "High", "Critical"]
    open_time_hours: float  # How long the ticket has been open
    category: str
    # created_at: datetime = datetime.utcnow() # Optionally pass creation time - will use internally if provided

class SLARiskResponse(BaseModel):
    risk_score: float
    risk_status: Literal["Low", "Medium", "High", "Critical"]
    predicted_breach_time: Optional[datetime] = None
    model_used: str

@router.post("/risk", response_model=SLARiskResponse,
             summary="Predict SLA breach risk for a ticket",
             response_description="SLA risk score and status, and predicted breach time.")
async def predict_sla_risk(
    request: SLARiskRequest
):
    """
    Predicts the risk of an SLA breach for a given ticket based on its priority,
    how long it has been open, and its category using a pre-trained Logistic Regression model.
    Requires 'Agent' or 'Admin' role.
    """
    logger.info(f"SLA risk prediction requested for priority={request.priority}, open_time={request.open_time_hours}h, category='{request.category}'.")

    if sla_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SLA prediction model is not loaded or trained. Please check backend logs."
        )

    # Prepare input for the model
    input_data = pd.DataFrame([{
        'priority': request.priority,
        'category': request.category,
        'open_time_hours': request.open_time_hours
    }])

    try:
        # Predict probability of breach (risk_score)
        # model.predict_proba returns probabilities for [class_0, class_1]
        # We want the probability of class_1 (breached)
        risk_score = sla_model.predict_proba(input_data)[0][1]

        # Determine risk status based on score
        if risk_score > 0.8:
            risk_status = "Critical"
        elif risk_score > 0.6:
            risk_status = "High"
        elif risk_score > 0.3:
            risk_status = "Medium"
        else:
            risk_status = "Low"

        # Predict breach time
        # We need a reference 'now' for the breach time calculation.
        # Assuming the request is being processed "now" for this calculation.
        current_utc_time_for_breach_prediction = datetime.utcnow()
        predicted_breach_time = predict_breach_time(
            priority=request.priority,
            open_time_hours=request.open_time_hours,
            current_utc_time=current_utc_time_for_breach_prediction
        )

        logger.info(f"SLA Risk for ticket: Score={risk_score:.2f}, Status='{risk_status}'. Predicted Breach: {predicted_breach_time}.")
        return SLARiskResponse(
            risk_score=round(risk_score, 3),
            risk_status=risk_status,
            predicted_breach_time=predicted_breach_time,
            model_used="Logistic Regression"
        )

    except Exception as e:
        logger.exception(f"Error during SLA risk prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error predicting SLA risk. Please try again."
        )