# buyerkraze

## Running with Docker

Prerequisites: [Docker](https://www.docker.com/) with Compose v2.

### Quick start

```bash
# 1. (Optional) configure environment variables
cp .env.example .env

# 2. Build and start the app
#    -> http://localhost:8000
#    -> http://localhost:8000/admin
docker compose up --build
```

On first start the container automatically:
- applies migrations
- collects static files
- creates a superuser if `DJANGO_SUPERUSER_USERNAME` is set

Useful commands:

```bash
docker compose down          # stop containers
docker compose logs -f web   # follow app logs
docker compose exec web python manage.py shell   # run a shell inside the container
docker compose exec web python manage.py makemigrations  # create a new migration
```

### Configuration

Settings are read from environment variables (optionally from a `.env` file).
See `.env.example` for all options.

- **SQLite** is used by default; the `db.sqlite3` file lives in the repo (kept
  via the bind mount) and media uploads persist in the `media_data` volume.
- To use **PostgreSQL** instead, set `DB_ENGINE=django.db.backends.postgresql`
  in `.env` and uncomment the `db` service in `docker-compose.yml`.
- For a **production-like** run (gunicorn, no source bind-mount), remove the
  `command:` and the `.:/app` volume from the `web` service in
  `docker-compose.yml`, set `DJANGO_DEBUG=false`, and use a real
  `DJANGO_SECRET_KEY`.
