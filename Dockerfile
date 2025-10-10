# ==== backend/Dockerfile ====
# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for NLTK and other tools if needed
# For 'punkt' and other NLTK data downloads that might need C compilers or similar,
# though 'slim-buster' usually has enough for basic NLTK.
# apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application into the container
COPY . .

# Create a directory for logs
RUN mkdir -p logs

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Run the Uvicorn server when the container starts
# Use 0.0.0.0 to listen on all available network interfaces
# --host 0.0.0.0 --port 8000 are often redundant with EXPOSE but good for explicit configuration
# The --reload flag should generally NOT be used in production for performance reasons.
# For production, remove --reload and potentially use gunicorn to manage uvicorn workers.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]