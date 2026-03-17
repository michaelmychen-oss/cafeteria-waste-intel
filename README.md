# Cafeteria Food Waste Intelligence System

AI-powered food waste tracking, prediction, and recommendation platform for school cafeterias.

## Architecture

```
Frontend (React + Vite)  →  Backend (FastAPI)  →  PostgreSQL
                                    ↓
                              Claude AI API
                         (extraction + analysis)
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL (or use SQLite for development — see below)
- Anthropic API key

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and Anthropic API key

# Start the server (auto-creates tables)
uvicorn app.main:app --reload --port 8000

# (Optional) Seed demo data
python seed_data.py
```

#### Using SQLite instead of PostgreSQL

For quick local development, change `DATABASE_URL` in `.env` to:
```
DATABASE_URL=sqlite:///./cafeteria_waste.db
```
Then change `psycopg2-binary` to `# psycopg2-binary` in requirements.txt.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies API calls to backend)
npm run dev
```

Open http://localhost:3000

### 3. Seed Data

To populate the database with demo schools and 30 days of sample data:
```bash
cd backend
python seed_data.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/schools/` | Create a school |
| GET | `/api/schools/` | List all schools |
| GET | `/api/schools/{id}` | Get school details |
| POST | `/api/reports/upload` | Upload & analyze a report |
| GET | `/api/reports/` | List reports (optional `?school_id=`) |
| GET | `/api/reports/{id}` | Get report details |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/dashboard/school/{id}/trend` | School waste trend |
| GET | `/api/dashboard/waste-records` | List waste records |

## Workflow

1. **Upload** → User uploads a cafeteria report (PDF, CSV, Excel, or image)
2. **Parse** → System extracts text/data from the file
3. **Extract** → Claude AI structures the data (menu items, quantities, dates)
4. **Analyze** → Claude AI identifies waste patterns and drivers
5. **Predict** → Rule-based engine classifies waste level
6. **Recommend** → Combined AI + rule-based recommendations
7. **Store** → All data persisted for historical analysis

## Project Structure

```
cafeteria-waste-intel/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI route handlers
│   │   │   ├── dashboard.py
│   │   │   ├── reports.py
│   │   │   └── schools.py
│   │   ├── core/          # Config, database setup
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/        # SQLAlchemy + Pydantic models
│   │   │   ├── api_models.py
│   │   │   └── schemas.py
│   │   ├── prompts/       # Claude AI prompt templates
│   │   │   └── templates.py
│   │   ├── services/      # Business logic
│   │   │   ├── ai_service.py
│   │   │   ├── parser.py
│   │   │   └── prediction.py
│   │   └── main.py        # FastAPI app entrypoint
│   ├── seed_data.py       # Demo data generator
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Upload.jsx
│   │   │   ├── Reports.jsx
│   │   │   └── Schools.jsx
│   │   ├── services/      # API client
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
└── docs/
    └── schema.sql         # Reference SQL schema
```

## Claude AI Prompts

The system uses four modular prompts (see `backend/app/prompts/templates.py`):

1. **Document Classification** — Categorizes uploaded documents (daily production, waste log, menu plan, etc.)
2. **Structured Data Extraction** — Pulls menu items, quantities, dates, and costs from raw text
3. **Waste Analysis** — Identifies waste levels, drivers, and generates recommendations
4. **Trend Analysis** — Analyzes historical patterns across schools for district-level insights

## Scaling to District-Wide Deployment

1. **Database** — Migrate to managed PostgreSQL (AWS RDS, Cloud SQL). Add read replicas for dashboard queries.
2. **File Storage** — Move uploads from local disk to S3/GCS with signed URLs.
3. **Async Processing** — Use Celery + Redis for background report processing. Return job ID on upload, poll for results.
4. **Auth** — Add JWT authentication with role-based access (district admin, school staff, read-only).
5. **Multi-tenancy** — Add `district_id` to isolate data between districts.
6. **Caching** — Redis cache for dashboard stats (refresh every 5 minutes).
7. **CI/CD** — Docker containers, deployed via GitHub Actions to AWS ECS or Cloud Run.
8. **Monitoring** — Structured logging, error tracking (Sentry), uptime monitoring.
9. **ML Upgrade** — Replace rule-based prediction with trained regression model using accumulated historical data (scikit-learn → XGBoost as data grows).
10. **Batch Uploads** — Support bulk CSV/Excel uploads covering multiple days/schools.
