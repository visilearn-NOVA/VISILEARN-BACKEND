# VisiLearn Deployment & Operations Guide

This guide provides deployment instructions and best practices for the **VisiLearn** student development team.

---

## 1. Quickstart: Local Docker Deployment

Run the complete stack (PostgreSQL + FastAPI + Alembic migrations) in containers:

```bash
# 1. Start containers in the background
docker-compose up --build -d

# 2. View logs
docker-compose logs -f backend

# 3. Test API availability
curl http://localhost:8000/health

# 4. Tear down containers when done
docker-compose down
```

The interactive API documentation is accessible at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 2. Manual Local Deployment (Without Docker)

### Prerequisites:
- Python 3.10+
- PostgreSQL 14+ installed and running on port 5432

### Step-by-Step:
```bash
# 1. Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Copy .env.example to .env and fill in your PostgreSQL credentials
cp .env.example .env

# 4. Apply database migrations
alembic upgrade head

# 5. Start development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 3. Production Deployment Options

### Option A: PaaS (Render / Railway / Fly.io) — Recommended for University Presentation
1. **Database**: Provision a managed PostgreSQL instance on Render or Railway.
2. **Environment Variables**: In the provider dashboard, configure:
   - `ENVIRONMENT="production"`
   - `DEBUG=false`
   - `SECRET_KEY`: Generate using `python -c "import secrets; print(secrets.token_hex(32))"`
   - `DATABASE_URL`: Set to the managed PostgreSQL connection string provided by the host.
   - `BACKEND_CORS_ORIGINS`: Set to your deployed frontend domain (e.g. `["https://visilearn.vercel.app"]`).
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option B: Cloud VM / VPS (AWS EC2 / DigitalOcean Droplet / Ubuntu Linux)
1. Install Docker & Docker Compose on the server.
2. Clone repository to `/var/www/visilearn-backend`.
3. Create `.env` file with production values.
4. Set up Nginx as a reverse proxy with Let's Encrypt SSL/TLS certificates (`certbot`).
5. Run `docker-compose -f docker-compose.yml up -d --build`.

---

## 4. Production Security Hardening Checklist

- [ ] **Secret Key**: Use a cryptographically secure 64-character hexadecimal key. Never commit `.env` to GitHub.
- [ ] **CORS**: Restrict `BACKEND_CORS_ORIGINS` to the exact frontend domain (do not use `*`).
- [ ] **Database Connection**: Use SSL mode (`sslmode=require`) when communicating with remote PostgreSQL databases.
- [ ] **Non-Root Execution**: Container runs under the unprivileged `visilearn` user.
- [ ] **Health Monitoring**: Monitor `/health` endpoint with uptime monitors.
