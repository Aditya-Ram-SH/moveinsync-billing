# Backend - MoveInSync Billing API

FastAPI-based backend for the MoveInSync Billing & Reporting Platform.

## 🚀 Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15 (via Docker)
- Virtual environment (recommended)

### Installation

```bash
# Create virtual environment
python -m venv cs
source cs/bin/activate  # On Windows: cs\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic python-jose[cryptography] passlib[bcrypt] python-multipart pydantic-settings
```

### Database Setup

1. **Start PostgreSQL** (via Docker):
   ```bash
   docker-compose up -d
   ```

2. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

3. **Seed Data** (optional):
   ```bash
   python seed_data.py
   python seed_trips.py
   ```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/              # Configuration, security, settings
│   │   ├── config.py      # Application settings
│   │   └── security.py    # JWT and password hashing
│   ├── db/                # Database configuration
│   │   ├── base.py        # SQLAlchemy base
│   │   ├── session.py     # Database session
│   │   └── schema.sql     # Database schema reference
│   ├── models.py          # SQLAlchemy ORM models
│   ├── routers/           # API route handlers
│   │   ├── auth_router.py
│   │   ├── billing_router.py
│   │   ├── contracts_router.py
│   │   ├── stats_router.py
│   │   └── trips_router.py
│   ├── schemas/           # Pydantic validation schemas
│   ├── services/          # Business logic
│   │   ├── billing_engine.py
│   │   └── audit.py
│   └── utils/             # Utility functions
│       ├── csv_import.py
│       └── username_mapping.py
├── alembic/               # Database migrations
│   └── versions/          # Migration files
├── seed_data.py          # Database seeding
└── requirements.txt      # Python dependencies
```

## 🔐 Authentication

The API uses JWT-based authentication:

1. **Login**: `POST /auth/token`
   - Returns JWT access token
   - Token expires in 24 hours (configurable)

2. **Protected Routes**: Include token in header
   ```
   Authorization: Bearer <token>
   ```

## 📊 API Endpoints

### Authentication
- `POST /auth/token` - Login
- `GET /auth/me` - Get current user info

### Contracts
- `GET /contracts` - List contracts
- `POST /contracts` - Create contract (Admin only)

### Trips
- `GET /trips/` - List trips
- `POST /trips/ingest-csv` - Upload CSV (Vendor/Admin)
- `GET /trips/employee/my-trips` - Employee's trips

### Billing
- `GET /billing/` - List billing runs
- `POST /billing/run` - Run billing (Admin only)
- `GET /billing/{id}/report` - Get billing report
- `GET /billing/{id}/export` - Export CSV report

### Statistics
- `GET /stats/dashboard` - Dashboard statistics
- `GET /stats/client-analytics` - Client analytics (Client only)
- `GET /stats/vendor-analytics` - Vendor analytics (Vendor only)

## 🗄️ Database Models

- **Users**: Authentication and RBAC
- **Clients**: Client companies
- **Vendors**: Vendor companies
- **Employees**: Employee records
- **Contracts**: Client-Vendor contracts with billing models
- **Trips**: Trip records
- **BillingRuns**: Monthly billing cycles
- **TripCharges**: Calculated charges per trip
- **AuditLogs**: Audit trail

## 🔄 Database Migrations

### Create Migration

```bash
alembic revision --autogenerate -m "description"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

## 🧪 Utility Scripts

- `seed_data.py` - Seed users, clients, vendors, contracts
- `seed_trips.py` - Seed sample trips
- `reset_database.py` - Clear all data (⚠️ destructive)
- `clear_billing_data.py` - Clear billing runs
- `verify_users.py` - Verify user accounts
- `generate_sample_csv.py` - Generate sample CSV
- `apply_billing_migration.py` - Manual migration helper

## 🔧 Configuration

Configuration is in `app/core/config.py`. Can be overridden with `.env` file:

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=password123
POSTGRES_DB=moveinsync_db
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:5173
```

## 📝 CSV Format

See `README_CSV_FORMAT.md` for trip CSV upload format details.

## 🐛 Troubleshooting

### Database Connection

```bash
# Check if PostgreSQL is running
docker ps

# Test connection
psql -U admin -d moveinsync_db -h localhost
```

### Migration Issues

```bash
# Check current migration version
alembic current

# Apply manually if needed
python apply_billing_migration.py
```

### Import Errors

```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
source cs/bin/activate

# Verify Python path
python -c "import app; print(app.__file__)"
```

## 📚 Dependencies

Key dependencies:
- `fastapi` - Web framework
- `sqlalchemy` - ORM
- `alembic` - Database migrations
- `psycopg2-binary` - PostgreSQL driver
- `python-jose` - JWT tokens
- `passlib` - Password hashing
- `pydantic` - Data validation

See `requirements.txt` for complete list.

