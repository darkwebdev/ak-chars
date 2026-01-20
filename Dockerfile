# Dockerfile for Fly.io deployment
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/

# Expose port (Fly.io uses 8080 by default)
EXPOSE 8080

# Start server
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8080"]
