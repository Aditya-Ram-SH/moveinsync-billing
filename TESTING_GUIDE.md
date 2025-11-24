# MoveInSync Billing Platform - Testing Guide

## 🎉 System Status: READY FOR TESTING

All core features have been implemented and are ready for testing!

---

## 📊 Database Status

### Seeded Data:
- ✅ **3 Clients**: TechCorp Solutions, Global Industries, MegaRetail Inc
- ✅ **4 Vendors**: SpeedyRides, SafeTravel, QuickMove, EliteFleet
- ✅ **15 Employees**: 5 per client
- ✅ **10 Users**: Admin, 3 clients, 4 vendors, 3 employees
- ✅ **4 Contracts**: One for each billing model (PACKAGE, TRIP, HYBRID_A, HYBRID_B)
- ✅ **88 Trips**: Sample trips for November 2025

---

## 🔑 Login Credentials

### Admin Access
- **Username**: `admin`
- **Password**: `admin123`
- **Permissions**: Full access to all features

### Client Users
- **Username**: `client1`, `client2`, `client3`
- **Password**: `client123`
- **Permissions**: View their own data only

### Vendor Users
- **Username**: `vendor1`, `vendor2`, `vendor3`, `vendor4`
- **Password**: `vendor123`
- **Permissions**: View their own data only

### Employee Users
- **Username**: `emp1`, `emp6`, `emp11`
- **Password**: `emp123`
- **Permissions**: View their own trips and incentives

---

## 🧪 Testing Workflow

### Step 1: Start the Backend
```bash
cd /home/boss_07/moveinsync_project/backend
source cs/bin/activate
uvicorn app.main:app --reload
```

### Step 2: Start the Frontend
```bash
cd /home/boss_07/moveinsync_project/frontend
npm run dev
```

### Step 3: Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## ✅ Test Cases

### 1. Authentication & Authorization
- [ ] Login as admin → Should see all data
- [ ] Login as client1 → Should see only client 1 data
- [ ] Login as vendor1 → Should see only vendor 1 data
- [ ] Login as emp1 → Should see only their trips and incentives
- [ ] Logout → Should redirect to login page

### 2. Dashboard
- [ ] View total clients, vendors, contracts, trips
- [ ] View recent billing run details
- [ ] Check role-based filtering (different stats for different roles)

### 3. Contracts
- [ ] View existing contracts
- [ ] Create a new contract (admin only)
- [ ] Test all 4 billing models (PACKAGE, TRIP, HYBRID_A, HYBRID_B)
- [ ] Verify dynamic form fields change based on model type

### 4. Trip Ingestion
- [ ] Upload CSV file with trip data
- [ ] Verify trips are ingested successfully
- [ ] Check trip status is "INGESTED"

### 5. Billing
- [ ] Run billing for November 2025
  - Client ID: 1, Vendor ID: 2 (TRIP model)
  - Client ID: 2, Vendor ID: 3 (HYBRID_A model)
  - Client ID: 3, Vendor ID: 4 (HYBRID_B model)
- [ ] Verify billing run completes successfully
- [ ] Check trip status changes to "PROCESSED"
- [ ] Export billing report as CSV
- [ ] Verify CSV contains correct calculations

### 6. Billing Logic Verification

#### PACKAGE Model (Fixed Monthly + Overage)
- [ ] Fixed fee is applied once per month
- [ ] Extra KM charges are calculated correctly
- [ ] Night shift bonuses are applied (trips between 10 PM - 6 AM)

#### TRIP Model (Pay-Per-Use)
- [ ] Base fare + distance rate is calculated
- [ ] Night multiplier is applied correctly
- [ ] Each trip is billed independently

#### HYBRID_A Model (Minimum Guarantee)
- [ ] Per-trip charges are calculated
- [ ] Minimum monthly guarantee is enforced
- [ ] If total < guarantee, difference is added

#### HYBRID_B Model (Base Distance Tier)
- [ ] Fixed base pay per trip is applied
- [ ] Extra distance beyond threshold is charged
- [ ] Calculations match the config

### 7. Employee Incentives
- [ ] Verify delay compensation is calculated
- [ ] Check delay threshold logic (e.g., 15 minutes)
- [ ] Confirm incentive amounts match config

### 8. Vendor Payouts
- [ ] Verify vendor payout calculations
- [ ] Check night shift bonuses
- [ ] Confirm overage charges

---

## 📝 Sample Test Data

### Test Billing Run 1: TRIP Model
```
Client ID: 1
Vendor ID: 2
Billing Month: 2025-11-01
Expected: ~22 trips processed
```

### Test Billing Run 2: HYBRID_A Model
```
Client ID: 2
Vendor ID: 3
Billing Month: 2025-11-01
Expected: ~22 trips processed + minimum guarantee check
```

### Test Billing Run 3: HYBRID_B Model
```
Client ID: 3
Vendor ID: 4
Billing Month: 2025-11-01
Expected: ~23 trips processed with base tier logic
```

---

## 🐛 Known Issues & Limitations

1. **Contract 1 (Client 1 + Vendor 1)**: No trips were seeded due to a mismatch in the seed script. This can be fixed by re-running the seed script or manually creating trips.

2. **Provisional Billing**: The system supports overwriting provisional billing runs, but the UI doesn't show a warning modal yet.

3. **CSV Format**: The trip CSV upload expects specific column names. Refer to `backend/app/utils/csv_import.py` for the expected format.

---

## 🎯 Key Features Implemented

### Backend (FastAPI + SQLAlchemy)
- ✅ JWT Authentication with bcrypt password hashing
- ✅ Role-Based Access Control (RBAC)
- ✅ Complete billing engine for all 4 models
- ✅ CSV trip ingestion
- ✅ Billing report export (CSV)
- ✅ Contract template API for dynamic forms
- ✅ Dashboard statistics with role-based filtering
- ✅ Audit logging for all operations
- ✅ Idempotent billing runs

### Frontend (React + Vite + TypeScript + shadcn/ui)
- ✅ Login page with JWT storage
- ✅ Protected routes
- ✅ Dashboard with real-time stats
- ✅ Contracts page with dynamic forms
- ✅ Trip ingestion page with CSV upload
- ✅ Billing page with run & export functionality
- ✅ Role-based navigation
- ✅ Responsive design with Tailwind CSS

---

## 📚 API Endpoints

### Authentication
- `POST /auth/login` - Login and get JWT token

### Contracts
- `GET /contracts` - List all contracts
- `GET /contracts/templates` - Get contract form templates
- `GET /contracts/{id}` - Get single contract
- `POST /contracts` - Create contract (admin only)

### Trips
- `POST /trips/ingest-csv` - Upload trip CSV

### Billing
- `GET /billing` - List billing runs
- `POST /billing/run` - Run billing cycle
- `GET /billing/{id}/export` - Export billing report

### Statistics
- `GET /stats/dashboard` - Get dashboard statistics (role-based)

### Health
- `GET /health` - Health check

---

## 🚀 Next Steps

1. **Test all user roles** and verify RBAC works correctly
2. **Run billing for all contracts** and verify calculations
3. **Export reports** and verify CSV format
4. **Test edge cases** (e.g., no trips, invalid dates, duplicate billing runs)
5. **Performance testing** with larger datasets
6. **UI/UX improvements** based on feedback
7. **Add charts/graphs** to the dashboard (optional)
8. **Deploy to production** (Railway, Vercel, etc.)

---

## 💡 Tips for Demo/Interview

1. **Start with the Dashboard** - Show the real-time stats
2. **Create a Contract** - Demonstrate the dynamic form generation
3. **Upload Trips** - Show the CSV ingestion
4. **Run Billing** - Execute a billing cycle and show the results
5. **Export Report** - Download the CSV and open it
6. **Switch Roles** - Login as different users to show RBAC
7. **Explain the Billing Logic** - Walk through the 4 models
8. **Highlight Architecture** - Multi-tenant, RBAC, audit logs, etc.

---

## 📞 Support

If you encounter any issues during testing, check:
1. Backend logs in the terminal
2. Frontend console in browser DevTools
3. Network tab for API errors
4. Database state in Adminer (http://localhost:8080)

Good luck with your interview! 🎉

