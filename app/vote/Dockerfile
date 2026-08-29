# Use a small official Python runtime image.
FROM python:3.11-slim

# Prevent Python from writing .pyc files and send logs directly to stdout/stderr.
#
# PROMETHEUS_MULTIPROC_DIR is required because Gunicorn runs multiple worker
# processes and the Prometheus Python client must aggregate metrics across them.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    GUNICORN_WORKERS=2 \
    PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc

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

# Create the directory used by Prometheus multiprocess mode.
RUN mkdir -p "${PROMETHEUS_MULTIPROC_DIR}" \
    && chown appuser:appgroup "${PROMETHEUS_MULTIPROC_DIR}"

# The application uses an unprivileged port because it runs as non-root.
EXPOSE 8080

# Use a dedicated health endpoint so automated probes do not count as
# real application page views.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --silent --show-error "http://127.0.0.1:${PORT}/healthz" || exit 1

USER appuser

# Remove stale Prometheus multiprocess files whenever the container starts,
# then launch Gunicorn with the worker cleanup configuration.
CMD ["sh", "-c", "rm -f ${PROMETHEUS_MULTIPROC_DIR}/* && exec gunicorn app:app \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:${PORT} \
    --workers ${GUNICORN_WORKERS} \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --timeout 30 \
    --graceful-timeout 30 \
    --keep-alive 2"]
