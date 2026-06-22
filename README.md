# Cashier Reports

Cashier Reports is a standalone Streamlit dashboard for the Cashier app. It
connects directly to the Postgres database with a read-only user and shows
monthly reporting charts without calling the Django API.

## Features

- Arabic, right-to-left dashboard UI.
- Orders tab: current-month total orders and revenue per day.
- Customers tab: current-month new and existing customers per day.
- Top customers section: top 10 customers by monthly revenue with order count.
- Most ordered meals tab: current-month top 3 ordered menu items per day.
- Cached aggregate SQL queries to reduce database load.
- Docker image build support for local and production deployment.

## Database Access

The app should use a read-only database user.

Required environment variables:

```env
REPORTS_DB_NAME=cashier
REPORTS_DB_USER=cashier_readonly
REPORTS_DB_PASSWORD=change-this-password
REPORTS_DB_HOST=db
REPORTS_DB_PORT=5432
```

The user only needs:

- `CONNECT` on the database
- `USAGE` on the `public` schema
- `SELECT` on application tables

From the infrastructure repo, you can create or update the local read-only user
with:

```bash
./devops/create_postgres_readonly_user.sh
```

For production, create the same read-only role on the production database and
set `REPORTS_DB_USER` and `REPORTS_DB_PASSWORD` before deploying.

## Run Locally

Install `uv`, then run the dashboard from this folder:

```bash
uv run streamlit run app.py
```

The app opens on:

```text
http://localhost:8501
```

## Run With Docker Compose

From the infrastructure repo:

```bash
docker compose up -d reports
```

Then open:

```text
http://localhost:8501
```

If the database volume already existed before the read-only user init script was
added, run:

```bash
./devops/create_postgres_readonly_user.sh
docker compose up -d reports
```

## Docker Image

Build locally:

```bash
docker build -t cashier-reports .
```

Run locally:

```bash
docker run --rm -p 8501:8501 \
  -e REPORTS_DB_NAME=cashier \
  -e REPORTS_DB_USER=cashier_readonly \
  -e REPORTS_DB_PASSWORD=change-this-password \
  -e REPORTS_DB_HOST=host.docker.internal \
  -e REPORTS_DB_PORT=5432 \
  cashier-reports
```

## Production Image Publishing

The GitHub Actions workflow in `.github/workflows/docker-publish.yml` builds and
pushes the image to GitHub Container Registry when changes are pushed to
`main`.

The production compose file expects this image:

```text
ghcr.io/fedal-nl/cashier_reports:latest
```

## Performance Notes

The dashboard uses monthly date filters and SQL aggregation in Postgres instead
of loading raw order history into Streamlit. Queries are cached for 5 minutes
with `st.cache_data`.

The reporting queries benefit from the existing order indexes on:

- `created_at`
- `created_at, status`
- `customer, created_at`

For the menu-item report, the query joins order items to orders and filters by
the order `created_at` range before ranking the top items per day.
