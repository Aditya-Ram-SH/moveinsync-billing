# MoveInSync Billing & Reporting Platform

A comprehensive billing and reporting platform for managing client-vendor relationships, trip tracking, and automated billing calculations.

## 🚀 Features

- **Role-Based Access Control (RBAC)**: Admin, Client, Vendor, and Employee roles
- **Contract Management**: Support for multiple billing models (Package, Trip, Hybrid A, Hybrid B)
- **Trip Ingestion**: CSV-based trip data import with validation
- **Automated Billing**: Monthly billing runs with idempotent processing
- **Analytics Dashboard**: Role-specific dashboards with interactive charts and visualizations
- **Employee Incentives**: Automatic incentive calculation and tracking
- **Audit Logging**: Complete audit trail for all operations

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 19 + TypeScript + Vite
- **Database**: PostgreSQL 15 (Docker)
- **ORM**: SQLAlchemy with Alembic migrations
- **Charts**: Recharts
- **UI**: Tailwind CSS + Radix UI

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11 or higher
- Node.js 18+ and npm
- PostgreSQL 15 (via Docker)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd moveinsync_project
```

### 2. Start PostgreSQL Database

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port `5432`
- Adminer (database admin UI) on port `8080`

**Database Credentials:**
- User: `admin`
- Password: `password123`
- Database: `moveinsync_db`

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv cs
source cs/bin/activate  # On Windows: cs\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic python-jose[cryptography] passlib[bcrypt] python-multipart pydantic-settings

# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python seed_data.py
python seed_trips.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 4. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 🔐 Demo Credentials

### Admin
- Username: `admin`
- Password: `admin123`

### Clients
- Username: `client1`, `client2`, `client3`
- Password: `client123`

### Vendors
- Username: `vendor1`, `vendor2`, `vendor3`, `vendor4`
- Password: `vendor123`

### Employees
- Username: `emp1`, `emp6`, `emp11`
- Password: `emp123`

## 📁 Project Structure

```
moveinsync_project/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration and security
│   │   ├── db/            # Database session and base
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── routers/       # API endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   ├── alembic/           # Database migrations
│   ├── seed_data.py       # Database seeding script
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── context/       # React context
│   │   └── pages/         # Page components
│   └── package.json       # Node dependencies
├── docker-compose.yml     # Docker configuration
└── new_schema.sql         # Database schema reference
```

## 🗄️ Database Setup

### Option 1: Using Schema File (Fresh Database)

```bash
# Connect to PostgreSQL
psql -U admin -d moveinsync_db -h localhost

# Run schema file
\i new_schema.sql
```

### Option 2: Using Alembic Migrations (Recommended)

```bash
cd backend
alembic upgrade head
```

### Option 3: Using Python Scripts

```bash
cd backend
python seed_data.py      # Creates users, clients, vendors, contracts
python seed_trips.py     # Creates sample trips
```

## 📊 Key Features Explained

### Billing Models

1. **PACKAGE**: Fixed monthly cost with included KM, extra KM charges
2. **TRIP**: Per-trip base fare + per KM rate
3. **HYBRID_A**: Monthly minimum + per trip base + per KM rate
4. **HYBRID_B**: Fixed trip pay + extra distance charges

### Billing Runs

- Monthly billing cycles based on year/month
- Idempotent: Running the same month twice won't duplicate charges
- Status tracking: RUNNING → SUCCESS/FAILED
- Automatic trip charge calculation

### Trip Ingestion

- CSV upload via frontend
- Validates contract, client, vendor relationships
- Supports employee assignment
- See `backend/README_CSV_FORMAT.md` for CSV format details

## 🔧 Development

### Backend Development

```bash
cd backend
source cs/bin/activate
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Database Migrations

```bash
cd backend
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🧪 Utility Scripts

Located in `backend/`:

- `seed_data.py` - Seed database with sample data
- `seed_trips.py` - Seed sample trips
- `reset_database.py` - Clear all data (⚠️ destructive)
- `clear_billing_data.py` - Clear billing runs and charges
- `verify_users.py` - Verify user accounts
- `verify_data_integrity.py` - Check data consistency
- `generate_sample_csv.py` - Generate sample CSV for trip ingestion

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎨 Frontend Routes

- `/` - Login page
- `/dashboard` - Role-specific dashboard
- `/contracts` - Contract management (Admin only)
- `/trips/ingest` - Trip CSV ingestion (Vendor/Admin)
- `/billing` - Billing run management (Admin only)

## 🔒 Environment Variables

Backend uses environment variables (optional, has defaults):

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=password123
POSTGRES_DB=moveinsync_db
SECRET_KEY=super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Create `.env` file in `backend/` directory to override defaults.

## 🐛 Troubleshooting

### Database Connection Issues

1. Ensure Docker container is running: `docker ps`
2. Check database credentials in `backend/app/core/config.py`
3. Verify port 5432 is not in use

### Migration Issues

```bash
# Reset Alembic version (if needed)
alembic stamp head

# Or apply migration manually
python apply_billing_migration.py
```

### Frontend Build Issues

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📄 License

See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for MoveInSync**

