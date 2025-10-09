# ==== backend/README.md ====
# TickIT AI Incident Management Backend

TickIT is an AI-powered platform designed to automate and streamline IT incident management. This backend service, built with FastAPI, provides robust APIs for ticket management, AI-driven classification, resolution recommendations, SLA prediction, anomaly detection, conversational AI, and dashboard analytics.

## Core Objectives

1.  **Automate** ticket creation, classification, routing, and resolution.
2.  **Recommend** fixes using AI similarity search.
3.  **Predict** SLA-breach risk and detect anomalies.
4.  Provide **analytics endpoints** for dashboards and a conversational assistant.

## Tech Stack

*   **Language:** Python 3.10+
*   **Framework:** FastAPI
*   **Database:** PostgreSQL (default) or SQLite (development) with SQLAlchemy ORM
*   **AI/ML:** `scikit-learn`, `sentence-transformers`, `Hugging Face` (models), `PyOD`, `FAISS`, `LangChain`, `OpenAI`/`Gemini`
*   **Auth:** JWT (Admin / Agent / EndUser roles)
*   **Vector store:** FAISS (local in-memory)
*   **Deployment:** Dockerfile included for containerization.

## Architecture