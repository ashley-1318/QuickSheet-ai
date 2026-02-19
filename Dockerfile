FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for cache
COPY requirements.txt .

# Install python dependencies without caching to save space
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Render sets PORT env variable)
ENV PORT=10000
EXPOSE $PORT

# Start application using shell form to interpolate PORT variable
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
