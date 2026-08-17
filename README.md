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

## Project Structure

The app now uses a small `src` layout so each concern has one clear place:

```text
src/
├── conf/        # database configuration and query execution
├── queries/     # SQL queries for the current PostgreSQL schema
├── repositories/# data-source contract, factory, and PostgreSQL adapter
├── services/    # reporting transformations against the repository contract
├── utils/       # date and formatting helpers
├── views/       # Streamlit rendering functions
└── main.py      # page composition and top-level app flow
```

The root `app.py` remains a thin Streamlit entrypoint so existing commands and
Docker configuration continue to work.

## Database Access

The app should use a read-only database user.

Required environment variables:

```env
REPORTS_DB_NAME=cashier
REPORTS_DB_USER=cashier_readonly
REPORTS_DB_PASSWORD=change-this-password
REPORTS_DB_HOST=db
REPORTS_DB_PORT=5432
REPORTS_REPOSITORY=postgres
REPORTS_DB_POOL_SIZE=5
REPORTS_DB_MAX_OVERFLOW=5
REPORTS_DB_POOL_RECYCLE=1800
```

The user only needs:

- `CONNECT` on the database
- `USAGE` on the `public` schema
- `SELECT` on application tables

`REPORTS_REPOSITORY` selects the data-source adapter and defaults to `postgres`.
To use the future ETL database, implement the `ReportingRepository` contract,
register that adapter in `src/repositories/factory.py`, and select it through
this environment variable. Views and services do not need to change.

Database access uses a process-wide SQLAlchemy connection pool. Connections are
validated before checkout, recycled after 30 minutes by default, and configured
as read-only PostgreSQL sessions. The pool settings above are optional.

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

## Run Unit Tests

The project uses Python's built-in `unittest` test runner for fast local checks.

```bash
uv run python -m unittest discover -s tests
```

## Run Test Coverage

Use the Make target below to run the unit tests inside the already running
`cashier_reports` application container and print a coverage summary. Coverage
excludes files under `tests/` and fails if application coverage drops below 95%.

```bash
make help
```

To run coverage:

```bash
make coverage
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
