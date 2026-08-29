#!/bin/sh
set -e

echo "==> Applying database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || echo "    (skipped collectstatic)"

# Optionally create a superuser on first boot (env-driven, non-interactive).
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
    echo "==> Creating superuser '${DJANGO_SUPERUSER_USERNAME}'..."
    python manage.py createsuperuser \
        --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "${DJANGO_SUPERUSER_EMAIL:-admin@buyerkraze.com}" \
        || echo "    (superuser already exists or creation failed)"
fi

echo "==> Starting server..."
exec "$@"
