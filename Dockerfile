# CloudViz Docker Configuration
FROM python:3.12-slim AS base

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

# Install Node.js for Mermaid CLI (alternative approach for environments with SSL issues)
RUN apt-get update && apt-get install -y ca-certificates \
    && apt-get install -y nodejs npm || ( \
        echo "Installing Node.js via alternative method..." \
        && apt-get install -y wget \
        && wget -qO- https://deb.nodesource.com/setup_20.x | bash - \
        && apt-get install -y nodejs \
    ) \
    && npm install -g @mermaid-js/mermaid-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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

# Default command
CMD ["python", "-m", "uvicorn", "cloudviz.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM base AS development

USER root
RUN pip install -r requirements/dev.txt
USER cloudviz

CMD ["python", "-m", "uvicorn", "cloudviz.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

# Copy production configuration
COPY config/prod.yml /app/config/default.yml

# Set production environment
ENV CLOUDVIZ_ENV=production

CMD ["python", "-m", "gunicorn", "cloudviz.api.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
