# ------------------------------------------------------------------
# BuyerKraze - Django web app
# ------------------------------------------------------------------
FROM python:3.11-slim

# Prevents Python from writing .pyc files and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# The entrypoint runs migrations / collectstatic, then launches the server
# passed as CMD (gunicorn by default; docker-compose overrides for dev).
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "buyerkraze.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
