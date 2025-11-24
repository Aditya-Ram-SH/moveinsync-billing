-- final_billing_schema_corrected.sql
-- Corrected, interview-ready PostgreSQL schema for MoveInSync case-study
-- Fixes applied: correct table creation order, valid trigger/function for billing_month, billing_runs placed before trips, trip/contract consistency trigger, contract date check, indexes, partitions notes.

-- ENUM types
CREATE TYPE role_enum AS ENUM ('ADMIN','CLIENT','VENDOR','EMPLOYEE');
CREATE TYPE status_enum AS ENUM ('ACTIVE','INACTIVE');
CREATE TYPE model_enum AS ENUM ('PACKAGE','TRIP','HYBRID');
CREATE TYPE trip_status_enum AS ENUM ('INGESTED','PROCESSED','ERROR');
CREATE TYPE trip_type_enum AS ENUM ('PICKUP','DROPOFF','INBOUND','OUTBOUND');
CREATE TYPE billing_status_enum AS ENUM ('RUNNING','SUCCESS','FAILED');
CREATE TYPE audit_entity_enum AS ENUM ('CONTRACT','BILLING_RUN');
CREATE TYPE audit_action_enum AS ENUM ('CREATE','UPDATE','DELETE');

-- 1. CLIENTS + VENDORS (must create before users)
CREATE TABLE clients (
  client_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  timezone TEXT DEFAULT 'UTC',
  status status_enum DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE vendors (
  vendor_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  contact_info TEXT,
  status status_enum DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. EMPLOYEES (optional)
CREATE TABLE employees (
  employee_id SERIAL PRIMARY KEY,
  client_id INT REFERENCES clients(client_id),
  full_name TEXT,
  email TEXT,
  phone TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. USERS + ROLES + TENANCY (after clients/vendors/employees)
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL, -- store bcrypt/argon2 hash in app
  role role_enum NOT NULL,
  client_id INT REFERENCES clients(client_id),
  vendor_id INT REFERENCES vendors(vendor_id),
  employee_id INT REFERENCES employees(employee_id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. CONTRACTS (versioned, JSONB config)
CREATE TABLE contracts (
  contract_id SERIAL PRIMARY KEY,
  client_id INT NOT NULL REFERENCES clients(client_id),
  vendor_id INT NOT NULL REFERENCES vendors(vendor_id),
  model_type model_enum NOT NULL,
  config_json JSONB NOT NULL,
  version INT NOT NULL DEFAULT 1,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_by INT REFERENCES users(user_id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT contracts_client_vendor_version_unique UNIQUE (client_id, vendor_id, version),
  CONSTRAINT chk_contract_dates CHECK (start_date <= end_date)
);

CREATE INDEX idx_contract_active ON contracts(is_active, start_date);
CREATE INDEX idx_contract_client_vendor ON contracts(client_id, vendor_id);

-- 5. BILLING RUNS (create before trips to allow FK from trips)
CREATE TABLE billing_runs (
  billing_run_id SERIAL PRIMARY KEY,
  client_id INT NOT NULL REFERENCES clients(client_id),
  vendor_id INT NOT NULL REFERENCES vendors(vendor_id),
  billing_month DATE NOT NULL, -- store first day of month
  triggered_by INT REFERENCES users(user_id),
  status billing_status_enum DEFAULT 'RUNNING',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  notes TEXT,
  CONSTRAINT uniq_billing_run UNIQUE (client_id, vendor_id, billing_month)
);

CREATE INDEX idx_billing_client_vendor ON billing_runs(client_id, vendor_id);
CREATE INDEX idx_billing_month ON billing_runs(billing_month);

-- Function + constraint trigger to enforce billing_month is first day
CREATE FUNCTION enforce_first_day_month() RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF date_trunc('month', NEW.billing_month) <> NEW.billing_month THEN
    RAISE EXCEPTION 'billing_month must be the first day of the month';
  END IF;
  RETURN NEW;
END;
$$;

CREATE CONSTRAINT TRIGGER chk_billing_month_firstday
  AFTER INSERT OR UPDATE ON billing_runs
  DEFERRABLE INITIALLY DEFERRED
  FOR EACH ROW
  EXECUTE FUNCTION enforce_first_day_month();

-- 6. TRIPS (parent partitioned table)
CREATE TABLE trips (
  trip_id SERIAL PRIMARY KEY,
  contract_id INT NOT NULL REFERENCES contracts(contract_id),
  client_id INT NOT NULL REFERENCES clients(client_id), -- denorm for fast queries
  vendor_id INT NOT NULL REFERENCES vendors(vendor_id), -- denorm for fast queries
  employee_id INT REFERENCES employees(employee_id),
  trip_type trip_type_enum DEFAULT 'INBOUND',
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL,
  distance_km NUMERIC(10,2) NOT NULL,
  distance_unit TEXT DEFAULT 'KM',
  duration_min INT NOT NULL,
  currency TEXT DEFAULT 'INR',
  raw_data JSONB NOT NULL,
  ingested_at TIMESTAMPTZ DEFAULT NOW(),
  status trip_status_enum DEFAULT 'INGESTED',
  billing_run_id INT REFERENCES billing_runs(billing_run_id)
) PARTITION BY RANGE (start_time);

-- Partition examples (create at deploy time)
-- CREATE TABLE trips_2025_11 PARTITION OF trips FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE INDEX idx_trips_contract ON trips(contract_id);
CREATE INDEX idx_trips_client ON trips(client_id);
CREATE INDEX idx_trips_vendor ON trips(vendor_id);
CREATE INDEX idx_trips_employee ON trips(employee_id);
CREATE INDEX idx_trips_start_time ON trips(start_time);

-- 7. TRIP CHARGES (partitioned by created_at)
CREATE TABLE trip_charges (
  charge_id SERIAL PRIMARY KEY,
  trip_id INT NOT NULL REFERENCES trips(trip_id),
  billing_run_id INT NOT NULL REFERENCES billing_runs(billing_run_id),
  base_cost NUMERIC(10,2),
  extra_km NUMERIC(10,2),
  extra_km_cost NUMERIC(10,2),
  extra_hours NUMERIC(10,2),
  extra_hours_cost NUMERIC(10,2),
  final_cost NUMERIC(10,2) NOT NULL,
  formula_snapshot JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Partition example
-- CREATE TABLE trip_charges_2025_11 PARTITION OF trip_charges FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE INDEX idx_trip_charges_run ON trip_charges(billing_run_id);

-- 8. AUDIT LOGS (simplified)
CREATE TABLE audit_logs (
  audit_id SERIAL PRIMARY KEY,
  entity_type audit_entity_enum NOT NULL,
  entity_id TEXT NOT NULL,
  action audit_action_enum NOT NULL,
  snapshot JSONB NOT NULL,
  performed_by INT REFERENCES users(user_id),
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  reason TEXT
);

-- 9. TRIGGERS
-- Ensure trips.client_id/vendor_id match the contract's client/vendor
CREATE FUNCTION fn_check_trip_contract_match() RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
  c_client INT;
  c_vendor INT;
BEGIN
  SELECT client_id, vendor_id INTO c_client, c_vendor FROM contracts WHERE contract_id = NEW.contract_id;
  IF c_client IS NULL OR c_vendor IS NULL THEN
    RAISE EXCEPTION 'contract % not found', NEW.contract_id;
  END IF;
  IF c_client <> NEW.client_id OR c_vendor <> NEW.vendor_id THEN
    RAISE EXCEPTION 'trip client_id/vendor_id do not match contract %', NEW.contract_id;
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_check_trip_contract_match
  BEFORE INSERT OR UPDATE ON trips
  FOR EACH ROW EXECUTE FUNCTION fn_check_trip_contract_match();

-- 10. HELPER CONSTRAINTS & INDEXES
CREATE INDEX IF NOT EXISTS idx_contracts_client_vendor_active ON contracts(client_id, vendor_id, is_active);
CREATE INDEX IF NOT EXISTS idx_trips_start_time_client ON trips(start_time, client_id);

-- 11. SAMPLE DATA (minimal)
INSERT INTO clients (name, timezone) VALUES ('Acme Corp', 'Asia/Kolkata');
INSERT INTO vendors (name, contact_info) VALUES ('FastRide', 'fast@rides.example');
INSERT INTO employees (client_id, full_name, email) VALUES (1, 'Ravi Kumar', 'ravi@example.com');

INSERT INTO users (username, password_hash, role, client_id, created_at) VALUES ('admin', 'HASHED_PASSWORD', 'ADMIN', NULL, NOW());

INSERT INTO contracts (client_id, vendor_id, model_type, config_json, start_date, end_date, created_by)
VALUES (1, 1, 'PACKAGE', '{"monthly_cost": 40000, "included_km": 1200, "extra_km_rate": 12}', '2025-11-01', '2026-04-30', 1);

-- Notes:
-- 1) Create monthly partitions for trips and trip_charges before inserting data for those months.
-- 2) Billing run should be implemented as: BEGIN TRANSACTION -> INSERT billing_runs -> SELECT trips for contract/month -> compute and INSERT trip_charges -> UPDATE trips SET billing_run_id -> COMMIT.
-- 3) Use application-level bcrypt/argon2 for password hashing.
-- 4) For demo, you can create partitions manually or write a migration that creates partitions for the needed months.
-- Only tiny optional tweak (not required): if you want faster ops dashboards later, you could add an index on billing_runs(status)

-- END of schema
