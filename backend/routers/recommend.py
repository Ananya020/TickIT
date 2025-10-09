# ==== backend/routers/recommend.py ====
import os
import json
import numpy as np
import faiss
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict

# SentenceTransformers for generating embeddings
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
    print("Warning: 'sentence-transformers' library not found. Recommendation engine will be mocked.")

from ..utils.logger import setup_logging
from ..dependencies import get_current_user, require_roles
from ..schemas.auth import UserRole

router = APIRouter()
logger = setup_logging()

# --- Configuration and Mock Knowledge Base ---
MODEL_NAME = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = "faiss_index.bin"
RESOLUTIONS_DATA_PATH = "resolutions.json"
EMBEDDING_DIMENSION = 384  # For all-MiniLM-L6-v2

# This mock data represents a simple knowledge base of past resolutions.
# In a real system, this would be populated from your database of resolved tickets.
MOCK_KNOWLEDGE_BASE = [
    {"description": "User cannot connect to VPN from home.", "resolution": "Instruct user to restart the VPN client and check their internet connection. Escalate if issue persists."},
    {"description": "The accounting software is running extremely slow.", "resolution": "Clear the application cache and advise the user to close other resource-intensive programs. Check for pending updates."},
    {"description": "My laptop screen is flickering constantly.", "resolution": "Advise user to update their graphics drivers from the manufacturer's website. If that fails, check the display cable connection."},
    {"description": "I forgot my password for the HR portal.", "resolution": "Guide user through the self-service password reset link on the login page. Provide a temporary password if the self-service fails."},
    {"description": "Printer is showing an 'offline' error message.", "resolution": "Verify the printer is powered on and connected to the network. Restart the printer and the print spooler service on the user's computer."},
    {"description": "Unable to access shared network drive.", "resolution": "Check if the user is connected to the company VPN. Verify their permissions for the specific network share."},
    {"description": "Application crashes on startup with error code 500.", "resolution": "This is a known issue. A patch is being deployed. Advise the user to wait for the update or use the web version as a workaround."},
    {"description": "Email is not syncing on my mobile device.", "resolution": "Instruct the user to remove and re-add their email account on the mobile device. Ensure server settings are correct."},
]

# --- Global Variables for Models and Data ---
sentence_model = None
faiss_index = None
resolutions_data = []

def build_and_save_faiss_index():
    """
    Builds a FAISS index from the mock knowledge base and saves it to disk.
    This function is called if the index file is not found on startup.
    """
    global resolutions_data
    logger.info(f"Building new FAISS index from knowledge base...")
    if not SentenceTransformer:
        logger.error("Cannot build FAISS index because 'sentence-transformers' is not installed.")
        return

    # Use the 'description' field to find similar problems.
    descriptions = [item["description"] for item in MOCK_KNOWLEDGE_BASE]
    resolutions_data = [item["resolution"] for item in MOCK_KNOWLEDGE_BASE]
    
    # Generate embeddings
    logger.info(f"Generating embeddings for {len(descriptions)} descriptions using '{MODEL_NAME}'...")
    embeddings = sentence_model.encode(descriptions, convert_to_tensor=False)
    
    # Create and populate FAISS index
    index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
    index.add(np.array(embeddings, dtype=np.float32))
    
    # Save index and resolutions to disk
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(RESOLUTIONS_DATA_PATH, 'w') as f:
        json.dump(resolutions_data, f)
        
    logger.info(f"FAISS index with {index.ntotal} vectors saved to '{FAISS_INDEX_PATH}'.")
    return index, resolutions_data

def load_faiss_index():
    """
    Loads the FAISS index and resolution data from disk on application startup.
    If files are not found, it triggers the build process.
    """
    global sentence_model, faiss_index, resolutions_data
    
    if os.getenv("SKIP_AI_INIT", "false").lower() == "true":
        logger.warning("Skipping FAISS index loading due to SKIP_AI_INIT=true.")
        return

    if not SentenceTransformer:
        logger.error("Cannot load FAISS index because 'sentence-transformers' is not installed.")
        return
        
    logger.info(f"Loading SentenceTransformer model: {MODEL_NAME}...")
    sentence_model = SentenceTransformer(MODEL_NAME)

    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(RESOLUTIONS_DATA_PATH):
        logger.info(f"Loading existing FAISS index from '{FAISS_INDEX_PATH}'.")
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        with open(RESOLUTIONS_DATA_PATH, 'r') as f:
            resolutions_data = json.load(f)
        logger.info(f"Successfully loaded index with {faiss_index.ntotal} vectors.")
    else:
        faiss_index, resolutions_data = build_and_save_faiss_index()

# Load the index on application startup
load_faiss_index()

# --- Pydantic Schemas for API ---
class RecommendationRequest(BaseModel):
    description: str = Field(..., min_length=10, example="My VPN is not connecting.")

class Recommendation(BaseModel):
    resolution: str = Field(..., example="Restart the VPN client.")
    similarity: float = Field(..., ge=0.0, le=1.0, example=0.91)

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]

def convert_distance_to_similarity(distance: float) -> float:
    """Converts L2 distance from FAISS to a more intuitive 0-1 similarity score."""
    # A simple inverse relationship. The divisor can be tuned based on typical distance values.
    # For normalized embeddings, max L2 distance is 2.
    similarity = max(0.0, 1.0 - (distance / 2.0))
    return round(similarity, 4)

# --- API Endpoint ---
@router.post("/resolution", response_model=RecommendationResponse,
             summary="Recommend resolutions for a ticket",
             response_description="A list of top 3 similar resolutions with similarity scores.",
             dependencies=[Depends(require_roles([UserRole.AGENT, UserRole.ADMIN]))])
async def recommend_resolution(
    request: RecommendationRequest,
    current_user: UserPayload = Depends(get_current_user)
):
    """
    Recommends potential resolutions based on the similarity of a new ticket's description
    to historical ticket data.

    **How it works:**
    1.  The system uses a `SentenceTransformer` model to convert the input ticket description into a numerical vector (embedding).
    2.  This embedding is then compared against a pre-indexed collection of embeddings from a historical knowledge base using FAISS (Facebook AI Similarity Search).
    3.  FAISS efficiently finds the top 3 most similar historical descriptions.
    4.  The resolutions corresponding to these historical tickets are returned with a calculated similarity score.

    **Future Enhancements:**
    -   **Connect to a Real Knowledge Base:** The `MOCK_KNOWLEDGE_BASE` can be replaced with a direct connection to the `tickets` table in the database. A background job could periodically query for resolved tickets, generate their embeddings, and update the FAISS index.
    -   **Use a Vector Database:** For larger-scale applications, the local FAISS index file could be replaced with a dedicated vector database like Pinecone, Weaviate, or Milvus for better scalability, management, and real-time updates.
    """
    logger.info(f"User {current_user.email} requested resolution recommendation for: '{request.description[:50]}...'")

    if not faiss_index or not sentence_model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation engine is not available. Check server logs."
        )

    # 1. Generate embedding for the input description
    query_embedding = sentence_model.encode([request.description])
    query_embedding_np = np.array(query_embedding, dtype=np.float32)
    
    # 2. Perform similarity search
    k = 3  # Number of recommendations to return
    distances, indices = faiss_index.search(query_embedding_np, k)
    
    # 3. Format the results
    recommendations = []
    for i in range(k):
        idx = indices[0][i]
        distance = distances[0][i]
        
        # Ensure the index is valid
        if idx < len(resolutions_data):
            recommendations.append(Recommendation(
                resolution=resolutions_data[idx],
                similarity=convert_distance_to_similarity(distance)
            ))

    if not recommendations:
        logger.warning(f"No recommendations found for: '{request.description[:50]}...'")

    return RecommendationResponse(recommendations=recommendations)