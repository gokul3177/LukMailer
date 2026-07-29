FROM python:3.11-slim

WORKDIR /app

# Install Node.js for building frontend assets
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Build React frontend
RUN cd frontend && npm install && npm run build

# Expose port 8000
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
