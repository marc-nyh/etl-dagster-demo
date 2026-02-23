# ETL Docker Demo — Dagster, Postgres & pgAdmin

A containerised ETL pipeline demonstrating ULD (Unit Load Device) data processing using **Dagster** for orchestration, **PostgreSQL** as the database, and **pgAdmin** for database inspection.

---

## 🏗️ Project Structure

```
etl-dagster-demo/
├── dagster/
│   └── etl_project/
│       ├── __init__.py          # Dagster Definitions entry point
│       ├── resources.py         # Shared resources (e.g. DB connection)
│       └── assets/
│           └── uld_assets.py    # ETL pipeline assets
├── sql/
│   ├── init/                    # ← Table schema (runs on first Postgres start)
│   │   └── 01_create_tables.sql
│   └── seed/                    # ← Sample data to populate tables
│       └── 01_seed_data.sql
├── docs/
│   └── NOTES.md                 # Personal learning notes (not for deployment)
└── docker-compose.yml
```

---

## 🚀 Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 1. Start all services

```bash
docker compose up -d --build
```

This spins up three containers:
| Container | Description | Port |
|---|---|---|
| `etl_postgres` | PostgreSQL database | `5432` |
| `etl_pgadmin` | pgAdmin UI | `5050` |
| `etl_dagster` | Dagster orchestrator + UI | `3000` |

---

## 🗄️ Database Initialisation

Tables and seed data are **not** loaded automatically when Postgres first starts.

Use Browser to access PgAdmin at **http://localhost:5050** to create tables and seed data.

To **Initialise tables**, use 01_create_tables.sql in sql/init/ folder.

To **Seed data**, use 01_seed_data.sql in sql/seed/ folder.


## ⚙️ Running the Pipeline

1. Open the Dagster UI at **http://localhost:3000**
2. Go to **Lineage** in the left sidebar.
3. Click **Materialize All** to run the full pipeline.

### Pipeline Flow

```
raw_uld_records          ← Extract from raw_uld table
      ↓
validated_uld_records    ← Split: valid vs invalid
      ↙              ↘
process_valid_records  process_invalid_records   ← Run in parallel
      ↘              ↙
   uld_processing_summary                        ← Report
can be viewed in the UI metadata
```

| Asset | Description |
|---|---|
| `raw_uld_records` | Reads all rows from `raw_uld` |
| `validated_uld_records` | Validates format; splits into two streams |
| `process_valid_records` | Enriches valid ULDs with airline names → `enriched_uld` |
| `process_invalid_records` | Attempts auto-repair (space removal); moves fixed records to `enriched_uld`, truly invalid to `invalid_uld` |
| `uld_processing_summary` | Reports counts: valid, auto-corrected, truly invalid |

---

## 🔍 Inspecting the Data

Open **pgAdmin** at **http://localhost:5050**

| Field | Value |
|---|---|
| Email | `admin@example.com` |
| Password | `admin` |

Connect to the server using:
- **Host**: `postgres`
- **Port**: `5432`
- **Username**: `etl_user`
- **Password**: `etl_password`
- **Database**: `etl_db`

---

## ⚠️ Corporate Network Note

If `docker compose build` fails with SSL errors, the `Dockerfile` uses `--trusted-host` pip flags to bypass corporate SSL inspection:

```dockerfile
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    --trusted-host pypi.python.org dagster dagster-webserver psycopg2-binary
```

This is acceptable for **local development only**. See `docs/NOTES.md` for alternatives.

---

## 💾 Data Persistence

Postgres data is stored in a Docker **Named Volume** (`postgres_data`).
On Mac, you cannot find Named Volumes directly in Finder as **Named Volume** files are stored inside a hidden linux virtual machine (VM) managed by docker.

On Windows, you can access these files via File Explorer using a network path while Docker is running:
```
\\wsl$\docker-desktop-data\data\docker\volumes\etl-dagster-demo_postgres_data\_data
```

> ⚠️ Do not edit files in this folder while the container is running — use pgAdmin instead.
You should not edit files directly but only through pgAdmin or Docker tools whenever possible.
