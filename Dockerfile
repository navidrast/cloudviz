# CloudViz Docker Configuration
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    graphviz \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Mermaid CLI
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @mermaid-js/mermaid-cli

# Create app user
RUN groupadd -r cloudviz && useradd -r -g cloudviz cloudviz

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements/ requirements/
RUN pip install -r requirements/prod.txt

# Copy application code
COPY . .

# Install CloudViz in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p logs output /app/config \
    && chown -R cloudviz:cloudviz /app

# Switch to non-root user
USER cloudviz

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - Use 0.0.0.0 in containers for external access
CMD ["python", "-m", "uvicorn", "cloudviz.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM base as development

USER root
RUN pip install -r requirements/dev.txt
USER cloudviz

CMD ["python", "-m", "uvicorn", "cloudviz.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy production configuration
COPY config/prod.yml /app/config/default.yml

# Set production environment
ENV CLOUDVIZ_ENV=production

CMD ["python", "-m", "gunicorn", "cloudviz.api.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
