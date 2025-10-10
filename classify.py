# backend/routers/classify.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import random # Keep if you want to fall back to random if model fails, but not for core logic
from typing import Optional, List # Import List for categories

from ..utils.logger import setup_logging
from ..dependencies import get_current_user, require_roles
from ..schemas.auth import UserRole
# Import the model and categories
from ..ml.classify_model import ticket_classifier_model, CLASSIFICATION_CATEGORIES

router = APIRouter()
logger = setup_logging()

class ClassificationRequest(BaseModel):
    description: str

class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    model_used: str
    # Optionally, you might want to return all probabilities
    # all_category_confidences: Optional[List[Dict[str, float]]] = None

@router.post("/ticket", response_model=ClassificationResponse,
             summary="Classify a ticket description",
             response_description="Predicted category and confidence score for the ticket.",
             dependencies=[Depends(require_roles([UserRole.AGENT, UserRole.ADMIN]))])
async def classify_ticket_description(
    request: ClassificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyzes a ticket description and predicts its category using a pre-trained TF-IDF + Logistic Regression model.
    Requires 'Agent' or 'Admin' role.
    """
    user_email = current_user['email'] if current_user else "anonymous"
    logger.info(f"User {user_email} requested classification for description: '{request.description[:50]}...'")

    if ticket_classifier_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ticket classification model is not loaded or trained. Please check backend logs."
        )

    try:
        # Predict the category and get probabilities
        # The pipeline handles both vectorization and classification
        probabilities = ticket_classifier_model.predict_proba([request.description])
        
        # Get the categories from the trained classifier's classes_ attribute
        # This ensures consistency between training and prediction
        model_categories = ticket_classifier_model.named_steps['clf'].classes_
        
        # Find the category with the highest probability
        predicted_category_index = probabilities.argmax(axis=1)[0]
        predicted_category = model_categories[predicted_category_index]
        confidence = probabilities[0][predicted_category_index]

        # Round confidence for cleaner output
        confidence = round(confidence, 3)

        model_used = "TF-IDF + Logistic Regression"

        logger.info(f"Classified ticket: Category='{predicted_category}', Confidence={confidence}, Model='{model_used}'.")
        return ClassificationResponse(
            category=predicted_category,
            confidence=confidence,
            model_used=model_used
        )

    except Exception as e:
        logger.exception(f"Error during ticket classification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error classifying ticket. Please try again."
        )