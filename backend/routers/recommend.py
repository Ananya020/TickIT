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
    {"id": "res16", "text": "Restart the affected service and monitor logs for errors.", "category": "Software Issue"},
    {"id": "res17", "text": "Check DNS configuration and resolve domain issues.", "category": "Network Problem"},
    {"id": "res18", "text": "Reset multi-factor authentication for the user.", "category": "Account Management"},
    {"id": "res19", "text": "Apply latest security patches to the server.", "category": "Security Incident"},
    {"id": "res20", "text": "Increase disk quota or free up space on the drive.", "category": "Performance Issue"},
    {"id": "res21", "text": "Verify SSL certificates are valid and not expired.", "category": "Security Incident"},
    {"id": "res22", "text": "Check event logs for critical errors and warnings.", "category": "Software Issue"},
    {"id": "res23", "text": "Replace defective power supply units.", "category": "Hardware Failure"},
    {"id": "res24", "text": "Confirm network switch is powered on and connected.", "category": "Network Problem"},
    {"id": "res25", "text": "Review application logs for exception stack traces.", "category": "Software Issue"},
    {"id": "res26", "text": "Reset the user's mailbox password.", "category": "Account Management"},
    {"id": "res27", "text": "Optimize database indexes for faster queries.", "category": "Performance Issue"},
    {"id": "res28", "text": "Run antivirus scans to detect malware.", "category": "Security Incident"},
    {"id": "res29", "text": "Check CPU and memory usage to identify bottlenecks.", "category": "Performance Issue"},
    {"id": "res30", "text": "Verify user is assigned to correct security groups.", "category": "Account Management"},
    {"id": "res31", "text": "Update firmware on network devices.", "category": "Network Problem"},
    {"id": "res32", "text": "Reinstall problematic software applications.", "category": "Software Issue"},
    {"id": "res33", "text": "Check for loose or damaged cables inside the server.", "category": "Hardware Failure"},
    {"id": "res34", "text": "Adjust firewall rules to allow necessary traffic.", "category": "Network Problem"},
    {"id": "res35", "text": "Enable logging for further diagnostics.", "category": "Software Issue"},
    {"id": "res36", "text": "Reset network adapter settings on the client machine.", "category": "Network Problem"},
    {"id": "res37", "text": "Verify backup jobs ran successfully.", "category": "Performance Issue"},
    {"id": "res38", "text": "Update antivirus definitions to latest version.", "category": "Security Incident"},
    {"id": "res39", "text": "Check hardware temperature sensors for overheating.", "category": "Hardware Failure"},
    {"id": "res40", "text": "Ensure correct proxy settings are configured.", "category": "Network Problem"},
    {"id": "res41", "text": "Provide user with instructions to reset account settings.", "category": "Account Management"},
    {"id": "res42", "text": "Run disk cleanup utilities to free up space.", "category": "Performance Issue"},
    {"id": "res43", "text": "Verify software license is valid and not expired.", "category": "Software Issue"},
    {"id": "res44", "text": "Test connectivity using ping and traceroute.", "category": "Network Problem"},
    {"id": "res45", "text": "Replace worn out or failing hard drives.", "category": "Hardware Failure"},
    {"id": "res46", "text": "Reboot the database server after maintenance.", "category": "Performance Issue"},
    {"id": "res47", "text": "Enable two-factor authentication for enhanced security.", "category": "Security Incident"},
    {"id": "res48", "text": "Check application configuration files for errors.", "category": "Software Issue"},
    {"id": "res49", "text": "Review server uptime and restart if necessary.", "category": "Performance Issue"},
    {"id": "res50", "text": "Update VPN server configuration to match new policies.", "category": "Network Problem"},
    {"id": "res51", "text": "Clean and reseat memory modules.", "category": "Hardware Failure"},
    {"id": "res52", "text": "Check print server and queue for stuck jobs.", "category": "Software Issue"},
    {"id": "res53", "text": "Audit user permissions to ensure least privilege.", "category": "Account Management"},
    {"id": "res54", "text": "Verify that backup power supplies are functioning.", "category": "Hardware Failure"},
    {"id": "res55", "text": "Review cloud service logs for anomalies.", "category": "Security Incident"},
    {"id": "res56", "text": "Reset browser settings to default for troubleshooting.", "category": "Software Issue"},
    {"id": "res57", "text": "Check DHCP server logs for lease issues.", "category": "Network Problem"},
    {"id": "res58", "text": "Upgrade server RAM for better performance.", "category": "Hardware Failure"},
    {"id": "res59", "text": "Check load balancer health and configuration.", "category": "Network Problem"},
    {"id": "res60", "text": "Schedule periodic maintenance tasks for optimization.", "category": "Performance Issue"},
]


# --- Sentence-Transformer and FAISS Setup ---
model_name = "all-MiniLM-L6-v2"
try:
    logger.info(f"Loading SentenceTransformer model: {model_name}...")
    sentence_model = SentenceTransformer(model_name)
    logger.info("SentenceTransformer model loaded.")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer model: {e}")
    sentence_model = None

faiss_index = None
resolution_texts = []
resolution_metadata = []

def initialize_faiss_index():
    global faiss_index, resolution_texts, resolution_metadata

    if sentence_model is None:
        logger.error("Cannot initialize FAISS index, SentenceTransformer model not loaded.")
        return

    logger.info("Initializing FAISS index with mock resolution data...")
    resolution_texts = [res["text"] for res in MOCK_RESOLUTIONS_DATA]
    resolution_metadata = MOCK_RESOLUTIONS_DATA

    embeddings = sentence_model.encode(resolution_texts, convert_to_numpy=True)
    dimension = embeddings.shape[1]

    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)
    logger.info(f"FAISS index initialized with {faiss_index.ntotal} resolutions.")

if os.getenv("SKIP_AI_INIT", "false").lower() != "true":
    initialize_faiss_index()
else:
    logger.warning("Skipping AI model and FAISS initialization due to SKIP_AI_INIT=true.")

# --- Request & Response Models ---
class RecommendationRequest(BaseModel):
    ticket_description: str
    category: Optional[str] = None

class ResolutionRecommendation(BaseModel):
    resolution_id: str
    text: str
    score: float
    category: Optional[str] = None

@router.post("/resolution", response_model=dict,
             summary="Recommend resolutions for a ticket description",
             response_description="A list of top 3 recommended resolutions with similarity scores.")
async def recommend_resolution(
    request: RecommendationRequest
):
    logger.info(f"Resolution recommendation requested for: '{request.ticket_description[:50]}...'")

    if faiss_index is None or sentence_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Recommendation service is not initialized. Please check backend logs."
        )

    query_embedding = sentence_model.encode([request.ticket_description], convert_to_numpy=True)

    k = 5
    distances, indices = faiss_index.search(query_embedding, k)

    recommendations = []
    seen_ids = set()

    for i, idx in enumerate(indices[0]):
        if len(recommendations) >= 3:
            break
        if idx >= len(resolution_metadata):
            logger.warning(f"FAISS index returned out-of-bounds index {idx}. Skipping.")
            continue

        res_data = resolution_metadata[idx]
        if res_data["id"] in seen_ids:
            continue

        if request.category and res_data.get("category") != request.category:
            continue

        distance = distances[0][i]
        similarity = max(0, 1 - (distance / 2.0))

        recommendations.append({
            "resolution_id": res_data["id"],
            "text": res_data["text"],
            "score": round(float(similarity), 3),
            "category": res_data.get("category")
        })
        seen_ids.add(res_data["id"])

    if not recommendations:
        logger.info(f"No relevant recommendations found for description: '{request.ticket_description[:50]}...'")
        random_recs = random.sample(MOCK_RESOLUTIONS_DATA, min(3, len(MOCK_RESOLUTIONS_DATA)))
        recommendations = [
            {
                "resolution_id": res["id"],
                "text": res["text"],
                "score": round(random.uniform(0.3, 0.6), 3),
                "category": res.get("category")
            } for res in random_recs
        ]
        logger.info(f"Returning {len(recommendations)} random fallback recommendations.")

    # 🔹 Wrap the list in an object with key 'recommendations'
    return {"recommendations": recommendations}
