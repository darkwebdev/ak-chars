# Dockerfile for Fly.io deployment
FROM python:3.11-slim

WORKDIR /app

# Trust Netskope/eBay certificates for corporate network
COPY netskope-certs.crt /usr/local/share/ca-certificates/netskope-certs.crt
RUN apt-get update && \
    apt-get install -y ca-certificates && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Configure Python/pip to trust certificates
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Install dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/

# Expose port (Fly.io uses 8080 by default)
EXPOSE 8080

# Start server
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8080"]
