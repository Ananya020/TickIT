# backend/ml/classify_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import os
import random

from ..utils.logger import setup_logging

logger = setup_logging()

MODEL_PATH = "backend/ml/ticket_classifier_pipeline.joblib"

# Categories to use for synthetic data and classification
CLASSIFICATION_CATEGORIES = [
    "Software Issue", "Hardware Failure", "Network Problem",
    "Account Management", "Security Incident", "Performance Issue",
    "Data Request", "Documentation Error", "General Inquiry" # Added a general category
]

# Simple mapping of keywords to categories for synthetic data generation
CATEGORY_KEYWORDS = {
    "Software Issue": ["bug", "error", "crash", "application", "software", "update", "feature"],
    "Hardware Failure": ["hardware", "desktop", "laptop", "printer", "monitor", "mouse", "keyboard", "device"],
    "Network Problem": ["network", "internet", "wifi", "connectivity", "vpn", "access", "connection"],
    "Account Management": ["password", "login", "account", "user", "access", "permission", "reset", "onboarding"],
    "Security Incident": ["phishing", "malware", "virus", "breach", "unauthorized", "suspicious", "security"],
    "Performance Issue": ["slow", "lag", "hang", "performance", "speed", "unresponsive", "load time"],
    "Data Request": ["data", "report", "extract", "query", "database", "analytics"],
    "Documentation Error": ["document", "guide", "manual", "kb", "training", "incorrect information"],
    "General Inquiry": ["question", "help", "information", "general", "query"]
}

def generate_synthetic_classification_data(num_samples=1000):
    """Generates synthetic ticket descriptions and categories."""
    data = []
    for _ in range(num_samples):
        category = random.choice(CLASSIFICATION_CATEGORIES)
        keywords = CATEGORY_KEYWORDS.get(category, [])
        num_keywords = random.randint(1, min(3, len(keywords))) # Pick 1-3 keywords
        selected_keywords = random.sample(keywords, num_keywords) if keywords else []

        # Add some noise words
        noise_words = random.sample(["the", "a", "is", "of", "and", "but", "it", "problem", "issue", "request", "please"], random.randint(2, 5))

        # Combine to form a description
        description_parts = selected_keywords + noise_words
        random.shuffle(description_parts)
        description = " ".join(description_parts) + "."

        # Introduce some variations and length
        if random.random() < 0.2: # Add more generic text for longer descriptions
            description += " I need assistance with this as soon as possible."
        if random.random() < 0.1: # Add a sentence from a different category to make it harder
            other_category = random.choice(CLASSIFICATION_CATEGORIES)
            if other_category != category:
                other_keywords = random.sample(CATEGORY_KEYWORDS.get(other_category, []), min(1, len(CATEGORY_KEYWORDS.get(other_category, []))))
                if other_keywords:
                    description += f" Also, there was a {other_keywords[0]}."

        data.append({"description": description, "category": category})

    df = pd.DataFrame(data)
    return df

def train_and_save_classifier(df):
    """Trains a TF-IDF + Logistic Regression pipeline and saves it."""
    X = df['description']
    y = df['category']

    # Create a text classification pipeline
    classifier_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)), # Limit features for simplicity
        ('clf', LogisticRegression(solver='liblinear', random_state=42, multi_class='auto', class_weight='balanced'))
    ])

    logger.info("Training ticket classification model...")
    classifier_pipeline.fit(X, y)
    logger.info("Model training complete.")

    # Save the trained model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(classifier_pipeline, MODEL_PATH)
    logger.info(f"Classifier pipeline saved to {MODEL_PATH}")

    return classifier_pipeline

def load_classifier():
    """Loads a pre-trained classification pipeline."""
    if os.path.exists(MODEL_PATH):
        logger.info(f"Loading ticket classification model from {MODEL_PATH}")
        return joblib.load(MODEL_PATH)
    logger.warning("No trained ticket classification model found. Please run training first.")
    return None

# --- Initialization on script load ---
ticket_classifier_model = None
try:
    if not os.path.exists(MODEL_PATH):
        logger.info("Generating synthetic data and training classification model for the first time...")
        synthetic_df = generate_synthetic_classification_data()
        ticket_classifier_model = train_and_save_classifier(synthetic_df)
    else:
        ticket_classifier_model = load_classifier()
except Exception as e:
    logger.error(f"Error during ticket classification model initialization: {e}")
    ticket_classifier_model = None