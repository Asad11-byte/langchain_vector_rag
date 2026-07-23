# Base image
FROM python:3.11-slim

# Prevents Python from writing .pyc files and buffers stdout (better logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps needed by unstructured/pypdf/docx2txt for parsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Most platforms (Render, Railway, Hugging Face Spaces) inject $PORT at runtime.
# Default to 7860 for Hugging Face Spaces; override via -e PORT=xxxx elsewhere.
ENV PORT=7860
EXPOSE 7860

# Use shell form so $PORT expands correctly at container start
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
