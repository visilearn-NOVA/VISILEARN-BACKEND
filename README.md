# VisiLearn: Student Performance Analytics System
> **Predicting and Visualising Academic Success**  
> University Group Project — Production-Ready Backend Architecture

---

## 📖 Overview

**VisiLearn** is a comprehensive academic analytics and predictive intelligence platform. It ingests student demographic, academic record, and behavioral questionnaire data to:
1. Provide personalized performance dashboards for students.
2. Deliver departmental cohort analytics for faculty and academic advisors.
3. Leverage an independent Machine Learning pipeline to predict academic success (GPA and performance tiers) and identify at-risk students for early intervention.

Built using **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**, and **Scikit-learn**, following clean architecture and separation of concerns.

---

## 🏗️ System Architecture

```
visilearn-backend/
├── app/
│   ├── main.py                 # FastAPI application entrypoint & middleware
│   ├── core/                   # Security (JWT, Argon2), config (Pydantic), dependencies
│   ├── database/               # PostgreSQL engine, sessionmaker, Base model
│   ├── models/                 # SQLAlchemy 2.0 ORM entity models
│   ├── schemas/                # Pydantic v2 validation and serialization schemas
│   ├── repositories/           # Isolated database query layer (CRUD)
│   ├── services/               # Business logic orchestration
│   ├── ml/                     # Decoupled machine learning predictor & preprocessors
│   ├── api/v1/                 # Versioned REST endpoints (auth, students, analytics, etc.)
│   └── utils/                  # Shared data parsers & helpers
├── alembic/                    # Database migrations management
├── tests/                      # Automated Pytest test suite
├── requirements.txt            # Python dependencies
├── .env.example                # Environment configuration template
└── README.md
```

---

## 🚀 Quickstart Guide for Development Team

### 1. Prerequisites
- **Python 3.10+** (verify with `python --version`)
- **PostgreSQL 14+** running locally or in Docker
- **Git**

### 2. Setup Virtual Environment
```bash
# Clone the repository
git clone <your-github-repo-url>
cd VISILEARN-BACKEND

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
# On Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# On Windows PowerShell:
Copy-Item .env.example .env

# On Linux / macOS:
cp .env.example .env
```
Open `.env` and verify your local PostgreSQL connection settings:
```env
POSTGRES_SERVER="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="your_postgres_password"
POSTGRES_DB="visilearn_db"
```

### 5. Create PostgreSQL Database
Using `psql` or pgAdmin, create the database:
```sql
CREATE DATABASE visilearn_db;
```

### 6. Run Database Migrations
```bash
# Run latest migrations
alembic upgrade head
```

### 7. Run the Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access the interactive API documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 👥 Student Team Git Workflow

To collaborate smoothly across the 3 team members:

1. **Main Branch Protection**:
   - `main`: Production-ready, stable codebase. Never push directly to `main`.
   - `develop`: Integration branch where team members merge feature branches.

2. **Feature Branching**:
   - `feature/auth-jwt`
   - `feature/student-academic-models`
   - `feature/ml-predictor-service`
   - `feature/analytics-endpoints`

3. **Pull Request Protocol**:
   - Create your feature branch from `develop`.
   - Test locally with `pytest`.
   - Open a Pull Request to `develop` and request at least one teammate review.
"# VISILEARN-BACKEND" 
