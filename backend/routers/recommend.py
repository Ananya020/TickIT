# ==== backend/routers/recommend.py ====
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import random
import numpy as np
from sentence_transformers import SentenceTransformer, util
import faiss
import os

from ..utils.logger import setup_logging
from ..dependencies import get_current_user, require_roles
from ..schemas.auth import UserRole

router = APIRouter()
logger = setup_logging()

# --- Mock Data for Resolution Recommendations ---
# In a real system, these would come from a database of past resolutions
MOCK_RESOLUTIONS_DATA = [
    {"id": "res1", "text": "Reboot the system and check network connectivity.", "category": "Network Problem"},
    {"id": "res2", "text": "Clear browser cache and cookies, then try again.", "category": "Software Issue"},
    {"id": "res3", "text": "Verify user credentials and reset password.", "category": "Account Management"},
    {"id": "res4", "text": "Update graphics drivers to the latest version.", "category": "Software Issue"},
    {"id": "res5", "text": "Check hard drive health using diagnostic tools.", "category": "Hardware Failure"},
    {"id": "res6", "text": "Ensure VPN client is connected and configured correctly.", "category": "Network Problem"},
    {"id": "res7", "text": "Grant necessary file permissions to the application directory.", "category": "Software Issue"},
    {"id": "res8", "text": "Replace faulty RAM modules.", "category": "Hardware Failure"},
    {"id": "res9", "text": "Review firewall rules for blocked ports.", "category": "Network Problem"},
    {"id": "res10", "text": "Escalate to security team for incident investigation.", "category": "Security Incident"},
    {"id": "res11", "text": "Instruct user to check spam folder for activation email.", "category": "Account Management"},
    {"id": "res12", "text": "Perform a clean install of the operating system.", "category": "Software Issue"},
    {"id": "res13", "text": "Check server load and resource utilization.", "category": "Performance Issue"},
    {"id": "res14", "text": "Consult the official documentation for setup instructions.", "category": "Documentation Error"},
    {"id": "res15", "text": "Verify physical cable connections for all devices.", "category": "Hardware Failure"},
]

# --- Sentence-Transformer and FAISS Setup ---
# This part would typically be initialized once at application startup.
# We'll make it global for simplicity in this example.
model_name = "all-MiniLM-L6-v2" # A good balance of speed and performance
# Check if model already exists locally to avoid re-downloading
try:
    logger.info(f"Loading SentenceTransformer model: {model_name}...")
    # This automatically downloads if not available
    sentence_model = SentenceTransformer(model_name)
    logger.info("SentenceTransformer model loaded.")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer model: {e}")
    sentence_model = None # Handle case where model loading fails

faiss_index = None
resolution_texts = []
resolution_metadata = []

def initialize_faiss_index():
    """
    Initializes and populates the FAISS index with mock resolution data.
    """
    global faiss_index, resolution_texts, resolution_metadata

    if sentence_model is None:
        logger.error("Cannot initialize FAISS index, SentenceTransformer model not loaded.")
        return

    logger.info("Initializing FAISS index with mock resolution data...")
    resolution_texts = [res["text"] for res in MOCK_RESOLUTIONS_DATA]
    resolution_metadata = MOCK_RESOLUTIONS_DATA

    # Generate embeddings for the mock resolutions
    embeddings = sentence_model.encode(resolution_texts, convert_to_numpy=True)
    dimension = embeddings.shape[1]

    # Create a FAISS index (e.g., IndexFlatL2 for L2 distance)
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)
    logger.info(f"FAISS index initialized with {faiss_index.ntotal} resolutions.")

# Initialize FAISS index on startup
if os.getenv("SKIP_AI_INIT", "false").lower() != "true":
    initialize_faiss_index()
else:
    logger.warning("Skipping AI model and FAISS initialization due to SKIP_AI_INIT=true.")


class RecommendationRequest(BaseModel):
    ticket_description: str
    category: Optional[str] = None # Optional: to filter recommendations by category

class ResolutionRecommendation(BaseModel):
    resolution_id: str
    resolution_text: str
    similarity_score: float
    category: Optional[str] = None

@router.post("/resolution", response_model=List[ResolutionRecommendation],
             summary="Recommend resolutions for a ticket description",
             response_description="A list of top 3 recommended resolutions with similarity scores.",
             dependencies=[Depends(require_roles([UserRole.AGENT, UserRole.ADMIN]))])
async def recommend_resolution(
    request: RecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Recommends potential resolutions based on the similarity of the ticket description
    to past resolution texts. Uses SentenceTransformer embeddings and FAISS search.
    Requires 'Agent' or 'Admin' role.
    """
    logger.info(f"User {current_user['email']} requested resolution recommendation for: '{request.ticket_description[:50]}...'")

    if faiss_index is None or sentence_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Recommendation service is not initialized. Please check backend logs."
        )

    # Generate embedding for the query description
    query_embedding = sentence_model.encode([request.ticket_description], convert_to_numpy=True)

    # Perform similarity search using FAISS
    k = 5 # Retrieve more than 3 to allow for filtering
    distances, indices = faiss_index.search(query_embedding, k)

    recommendations = []
    seen_ids = set() # To avoid duplicate recommendations if filtering causes issues

    for i, idx in enumerate(indices[0]):
        if len(recommendations) >= 3: # Limit to top 3
            break

        if idx >= len(resolution_metadata): # Should not happen with correctly built index
            logger.warning(f"FAISS index returned out-of-bounds index {idx}. Skipping.")
            continue

        res_data = resolution_metadata[idx]
        if res_data["id"] in seen_ids:
            continue

        # Optional: Filter by category if provided in the request
        if request.category and res_data.get("category") != request.category:
            continue

        # Convert FAISS distance (L2) to a similarity score (0-1)
        # Higher distance means lower similarity. We need to invert this.
        # A common way is to use exp(-distance) or 1 / (1 + distance)
        # For this example, let's just scale based on min/max plausible distances, or a simpler inverse.
        # Note: L2 distance is not directly cosine similarity. For cosine, FAISS IndexFlatIP can be used
        # For simplicity, we'll map L2 distance to a pseudo-similarity.
        # Max distance could be ~2.0 for normalized embeddings if they are exactly opposite.
        # Min distance is 0.0 for identical embeddings.
        distance = distances[0][i]
        # A simple inverse mapping:
        similarity = max(0, 1 - (distance / 2.0)) # Assuming max L2 distance is around 2 for normalized vectors

        recommendations.append(ResolutionRecommendation(
            resolution_id=res_data["id"],
            resolution_text=res_data["text"],
            similarity_score=round(float(similarity), 3),
            category=res_data.get("category")
        ))
        seen_ids.add(res_data["id"])

    if not recommendations:
        logger.info(f"No relevant recommendations found for description: '{request.ticket_description[:50]}...'")
        # As a fallback, provide random recommendations if no good matches are found
        # Or return an empty list if strictness is preferred.
        # For now, let's return a few random ones if nothing specific matched.
        random_recs = random.sample(MOCK_RESOLUTIONS_DATA, min(3, len(MOCK_RESOLUTIONS_DATA)))
        recommendations = [
            ResolutionRecommendation(
                resolution_id=res["id"],
                resolution_text=res["text"],
                similarity_score=round(random.uniform(0.3, 0.6), 3), # Lower confidence for fallback
                category=res.get("category")
            ) for res in random_recs
        ]
        logger.info(f"Returning {len(recommendations)} random fallback recommendations.")

    return recommendations