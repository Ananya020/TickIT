# ==== backend/routers/sla.py ====
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import random
from datetime import datetime, timedelta
from typing import Literal
from typing import Optional
from datetime import datetime

from ..utils.logger import setup_logging
from ..dependencies import get_current_user, require_roles
from ..schemas.auth import UserRole

router = APIRouter()
logger = setup_logging()

class SLARiskRequest(BaseModel):
    priority: Literal["Low", "Medium", "High", "Critical"]
    open_time_hours: float  # How long the ticket has been open
    category: str
    # created_at: datetime = datetime.utcnow() # Optionally pass creation time

class SLARiskResponse(BaseModel):
    risk_score: float
    risk_status: Literal["Low", "Medium", "High", "Critical"]
    predicted_breach_time: Optional[datetime] = None
    model_used: str

# Mock SLA definitions (in hours)
SLA_DEFINITIONS = {
    "Critical": 4,
    "High": 8,
    "Medium": 24,
    "Low": 48
}

@router.post("/risk", response_model=SLARiskResponse,
             summary="Predict SLA breach risk for a ticket",
             response_description="SLA risk score and status, and predicted breach time.",
             dependencies=[Depends(require_roles([UserRole.AGENT, UserRole.ADMIN]))])
async def predict_sla_risk(
    request: SLARiskRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Predicts the risk of an SLA breach for a given ticket based on its priority,
    how long it has been open, and its category.
    Mocks a Logistic Regression model.
    Requires 'Agent' or 'Admin' role.
    """
    logger.info(f"User {current_user['email']} requested SLA risk prediction for priority={request.priority}, open_time={request.open_time_hours}h, category='{request.category}'.")

    # --- MOCK ML MODEL LOGIC ---
    # In a real scenario:
    # 1. Load your pre-trained Logistic Regression model.
    # 2. Encode categorical features (priority, category) into numerical format.
    # 3. Use the model to predict the risk score.
    #   features = [
    #       one_hot_encode(request.priority),
    #       request.open_time_hours,
    #       one_hot_encode(request.category)
    #   ]
    #   risk_score = log_reg_model.predict_proba([features])[0][1] # Probability of breach

    base_sla_hours = SLA_DEFINITIONS.get(request.priority, 48)

    # Factors influencing risk:
    # 1. Proximity to SLA deadline
    # 2. Priority itself
    # 3. Category (some categories might be historically riskier, mocked here)

    # Calculate current progress towards SLA
    progress_ratio = request.open_time_hours / base_sla_hours

    # Base risk score based on progress (0.0 to 1.0)
    risk_score = min(1.0, max(0.0, progress_ratio * 0.8 + random.uniform(-0.1, 0.1))) # Add some randomness

    # Adjust for category (mocked)
    if "Security" in request.category or "Network" in request.category:
        risk_score += 0.1
    if "Software" in request.category and request.open_time_hours > 12:
        risk_score += 0.05

    risk_score = max(0.0, min(1.0, risk_score)) # Ensure score is between 0 and 1

    # Determine risk status
    if risk_score > 0.8:
        risk_status = "Critical"
    elif risk_score > 0.6:
        risk_status = "High"
    elif risk_score > 0.3:
        risk_status = "Medium"
    else:
        risk_status = "Low"

    # Predict breach time if applicable
    predicted_breach_time = None
    if progress_ratio < 1.0: # If not already breached
        remaining_time_hours = base_sla_hours - request.open_time_hours
        # For simplicity, we assume creation_time is 'now' if not provided
        # In a real scenario, created_at from the actual ticket would be used
        predicted_breach_time = datetime.utcnow() + timedelta(hours=remaining_time_hours)
    else:
        # If open_time_hours already exceeds SLA, it's considered breached
        # We can set predicted_breach_time to a past time or just leave it None/indicate already breached.
        # For this mock, if already breached, we can infer it
        pass


    logger.info(f"SLA Risk for ticket: Score={risk_score:.2f}, Status='{risk_status}'.")
    return SLARiskResponse(
        risk_score=round(risk_score, 3),
        risk_status=risk_status,
        predicted_breach_time=predicted_breach_time,
        model_used="Mock Logistic Regression"
    )