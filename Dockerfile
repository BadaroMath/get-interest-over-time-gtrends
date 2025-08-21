# Google Trends Analyzer Docker Image

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install -e .

# Create directories for data and configs
RUN mkdir -p /data/results /data/cache /data/config

# Set environment variables
ENV TRENDS_CACHE_DIR=/data/cache
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 trends-user && \
    chown -R trends-user:trends-user /app /data

USER trends-user

# Default command
CMD ["trends-analyzer", "--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import trends_analyzer; print('OK')" || exit 1

# Labels
LABEL maintainer="your.email@example.com"
LABEL version="1.0.0"
LABEL description="Google Trends Analyzer - A comprehensive toolkit for Google Trends data analysis"