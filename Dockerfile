# Use a small official Python image
FROM python:3.12-slim

# Where the app will live inside the container
WORKDIR /app

# Install system dependencies if needed (optional at first)
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy dependency list first (better for Docker layer caching)
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Expose the port the app listens on *inside* the container
EXPOSE 8000

# Default command: run Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
