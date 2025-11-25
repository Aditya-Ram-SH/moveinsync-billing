# Setup Guide - MoveInSync Billing Platform

Complete step-by-step setup guide for first-time installation.

## 📋 Prerequisites Checklist

- [ ] Docker Desktop installed and running
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ and npm installed
- [ ] Git installed

## 🚀 Step-by-Step Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd moveinsync_project
```

### Step 2: Start Database

```bash
# Start PostgreSQL container
docker-compose up -d

# Verify it's running
docker ps
```

You should see `mis_db` container running. Database is now available at `localhost:5432`.

**Optional**: Access Adminer UI at `http://localhost:8080`
- System: PostgreSQL
- Server: `db`
- Username: `admin`
- Password: `password123`
- Database: `moveinsync_db`

### Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv cs

# Activate virtual environment
# On Linux/Mac:
source cs/bin/activate
# On Windows:
cs\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Or install manually:
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic python-jose[cryptography] passlib[bcrypt] python-multipart pydantic-settings
```

### Step 4: Initialize Database

```bash
# Option A: Using Alembic (Recommended)
alembic upgrade head

# Option B: Using schema file
psql -U admin -d moveinsync_db -h localhost -f ../new_schema.sql

# Option C: Using Python (creates tables automatically)
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"
```

### Step 5: Seed Initial Data

```bash
# Seed users, clients, vendors, contracts
python seed_data.py

# Seed sample trips (optional)
python seed_trips.py

# Verify users
python verify_users.py
```

### Step 6: Start Backend Server

```bash
# Make sure virtual environment is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should be running at `http://localhost:8000`
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### Step 7: Setup Frontend

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend should be running at `http://localhost:5173`

### Step 8: Login

Open browser: `http://localhost:5173`

Use demo credentials:
- **Admin**: `admin` / `admin123`
- **Client**: `client1` / `client123`
- **Vendor**: `vendor1` / `vendor123`
- **Employee**: `emp1` / `emp123`

## ✅ Verification

### Check Backend

```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status":"ok"}
```

### Check Database

```bash
# Connect to database
psql -U admin -d moveinsync_db -h localhost

# Check tables
\dt

# Check users
SELECT username, role FROM users;
```

### Check Frontend

- Open `http://localhost:5173`
- Should see login page
- Login with demo credentials
- Should see dashboard

## 🔧 Common Issues

### Issue: Docker container won't start

```bash
# Check if port 5432 is in use
lsof -i :5432  # Mac/Linux
netstat -ano | findstr :5432  # Windows

# Stop existing PostgreSQL if needed
docker-compose down
docker-compose up -d
```

### Issue: Database connection error

1. Verify Docker container is running: `docker ps`
2. Check credentials in `backend/app/core/config.py`
3. Test connection: `psql -U admin -d moveinsync_db -h localhost`

### Issue: Migration errors

```bash
# Check current migration state
alembic current

# If needed, apply migration manually
python apply_billing_migration.py
```

### Issue: Frontend can't connect to backend

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `backend/app/core/config.py`
3. Verify frontend API URL in `frontend/src/api/axios.ts`

### Issue: Module not found errors

```bash
# Ensure virtual environment is activated
source cs/bin/activate  # or cs\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

## 🎯 Next Steps

1. **Explore the Dashboard**: Login and check role-specific dashboards
2. **Create Contracts**: Login as admin and create contracts
3. **Ingest Trips**: Upload CSV files with trip data
4. **Run Billing**: Execute billing runs for different months
5. **View Reports**: Check billing reports and analytics

## 📚 Additional Resources

- Main README: `README.md`
- Backend README: `backend/README.md`
- CSV Format: `backend/README_CSV_FORMAT.md`
- API Docs: `http://localhost:8000/docs` (when backend is running)

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review error messages in terminal/logs
3. Verify all prerequisites are installed
4. Check Docker container status
5. Review database connection settings

---

**Happy Coding! 🚀**

