# Use a small official Python runtime image.
FROM python:3.11-slim

# Prevent Python from writing .pyc files and send logs directly to stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    GUNICORN_WORKERS=2

# Install curl for the container health check, then remove APT metadata.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create a dedicated non-root user for the application.
RUN groupadd --system --gid 10001 appgroup \
    && useradd \
        --system \
        --uid 10001 \
        --gid appgroup \
        --create-home \
        --home-dir /home/appuser \
        appuser

WORKDIR /usr/local/app

# Copy and install dependencies separately for efficient Docker layer caching.
COPY requirements.txt .

RUN pip install \
        --no-cache-dir \
        --disable-pip-version-check \
        -r requirements.txt

# Copy the application source and assign ownership to the non-root user.
COPY --chown=appuser:appgroup . .

# The application uses an unprivileged port because it runs as non-root.
EXPOSE 8080

# Check that the web process can answer HTTP requests.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --silent --show-error "http://127.0.0.1:${PORT}/" || exit 1

USER appuser

# Use exec so Gunicorn receives container stop signals correctly.
# PORT and GUNICORN_WORKERS remain configurable at runtime.
CMD ["sh", "-c", "exec gunicorn app:app \
    --bind 0.0.0.0:${PORT} \
    --workers ${GUNICORN_WORKERS} \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --timeout 30 \
    --graceful-timeout 30 \
    --keep-alive 2"]
