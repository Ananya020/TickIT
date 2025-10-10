# backend/routers/sla_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os
from datetime import datetime, timedelta
import random
from datetime import datetime, timedelta
from typing import Optional
import random
import logging

from ..utils.logger import setup_logging

logger = setup_logging()

# --- SLA Definitions (in hours) ---
SLA_DEFINITIONS = {
    "Critical": 4,
    "High": 8,
    "Medium": 24,
    "Low": 48
}

MODEL_PATH = "backend/ml/sla_logistic_regression_model.joblib"

def generate_synthetic_data(num_samples=1000):
    """Generates synthetic data for SLA breach prediction."""
    priorities = ["Low", "Medium", "High", "Critical"]
    categories = ["IT Support", "Bug", "Feature Request", "Security", "Network", "Software"]

    data = []
    for _ in range(num_samples):
        priority = random.choice(priorities)
        category = random.choice(categories)
        base_sla = SLA_DEFINITIONS.get(priority, 48)

        # Generate open_time_hours relative to SLA
        # Introduce some tickets that are close to breach or past breach
        if random.random() < 0.3: # 30% are close to or over SLA
            open_time_hours = random.uniform(base_sla * 0.7, base_sla * 1.5)
        else: # 70% are well within SLA
            open_time_hours = random.uniform(0.1, base_sla * 0.8)

        # Determine if breached based on open_time_hours vs. base_sla
        breached = 1 if open_time_hours >= base_sla else 0

        data.append({
            "priority": priority,
            "category": category,
            "open_time_hours": open_time_hours,
            "breached": breached,
            "base_sla_hours": base_sla # For later breach time calculation
        })

    df = pd.DataFrame(data)
    return df

def train_and_save_model(df):
    """Trains a Logistic Regression model and saves it."""
    # Define features and target
    X = df[['priority', 'category', 'open_time_hours']]
    y = df['breached']

    # Define categorical and numerical features
    categorical_features = ['priority', 'category']
    numerical_features = ['open_time_hours']

    # Create a column transformer for preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ])

    # Create the pipeline with preprocessing and logistic regression
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(solver='liblinear', random_state=42, class_weight='balanced'))
    ])

    # Train the model
    logger.info("Training SLA risk prediction model...")
    model_pipeline.fit(X, y)
    logger.info("Model training complete.")

    # Save the trained model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model_pipeline, MODEL_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")

    return model_pipeline

def load_model():
    """Loads a pre-trained model."""
    if os.path.exists(MODEL_PATH):
        logger.info(f"Loading SLA risk prediction model from {MODEL_PATH}")
        return joblib.load(MODEL_PATH)
    logger.warning("No trained SLA model found. Please run training first.")
    return None

def predict_breach_time(priority: str, open_time_hours: float, current_utc_time: datetime = None) -> Optional[datetime]:
    """
    Predicts the exact time of breach.
    Assumes the current_utc_time is the reference point for 'now'.
    """
    if current_utc_time is None:
        current_utc_time = datetime.utcnow()

    base_sla_hours = SLA_DEFINITIONS.get(priority, 48)

    # If already past SLA, no future breach time
    if open_time_hours >= base_sla_hours:
        return None

    remaining_time_hours = base_sla_hours - open_time_hours
    predicted_breach_time = current_utc_time + timedelta(hours=remaining_time_hours)
    return predicted_breach_time

# --- Initialization on script load ---
sla_model = None
try:
    if not os.path.exists(MODEL_PATH):
        logger.info("Generating synthetic data and training model for the first time...")
        synthetic_df = generate_synthetic_data()
        sla_model = train_and_save_model(synthetic_df)
    else:
        sla_model = load_model()
except Exception as e:
    logger.error(f"Error during SLA model initialization: {e}")
    sla_model = None