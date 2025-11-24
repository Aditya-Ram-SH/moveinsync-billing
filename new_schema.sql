-- =========================================================
-- FINAL MOVEINSYNC BILLING PLATFORM SCHEMA
-- Clean, simple, production-safe, matches backend + UI
-- =========================================================

-- 1. ENUMS
CREATE TYPE role_enum AS ENUM ('ADMIN','CLIENT','VENDOR','EMPLOYEE');
CREATE TYPE status_enum AS ENUM ('ACTIVE','INACTIVE');
CREATE TYPE model_enum AS ENUM ('PACKAGE','TRIP','HYBRID_A','HYBRID_B');
CREATE TYPE trip_status_enum AS ENUM ('INGESTED','PROCESSED','ERROR');
CREATE TYPE trip_type_enum AS ENUM ('PICKUP','DROPOFF','INBOUND','OUTBOUND');
CREATE TYPE billing_status_enum AS ENUM ('RUNNING','SUCCESS','FAILED');
CREATE TYPE audit_action_enum AS ENUM ('CREATE','UPDATE','DELETE');

-- 2. CLIENTS
CREATE TABLE clients (
  client_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  timezone TEXT DEFAULT 'UTC',
  status status_enum DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. VENDORS
CREATE TABLE vendors (
  vendor_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  contact_info TEXT,
  status status_enum DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. EMPLOYEES
CREATE TABLE employees (
  employee_id SERIAL PRIMARY KEY,
  client_id INT REFERENCES clients(client_id),
  full_name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. USERS (RBAC)
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role role_enum NOT NULL,
  client_id INT REFERENCES clients(client_id),
  vendor_id INT REFERENCES vendors(vendor_id),
  employee_id INT REFERENCES employees(employee_id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. CONTRACTS (Versioned + Unified + JSON Config)
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
  CONSTRAINT uniq_contract_version UNIQUE (client_id, vendor_id, version),
  CONSTRAINT chk_contract_dates CHECK (start_date <= end_date)
);

CREATE INDEX idx_contract_active ON contracts(is_active);
CREATE INDEX idx_contract_client_vendor ON contracts(client_id, vendor_id);

-- 7. BILLING RUNS (Idempotent)
CREATE TABLE billing_runs (
  billing_run_id SERIAL PRIMARY KEY,
  client_id INT NOT NULL REFERENCES clients(client_id),
  vendor_id INT NOT NULL REFERENCES vendors(vendor_id),
  billing_month DATE NOT NULL,
  triggered_by INT REFERENCES users(user_id),
  status billing_status_enum DEFAULT 'RUNNING',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  notes TEXT,
  CONSTRAINT uniq_billing_run UNIQUE (client_id, vendor_id, billing_month)
);

CREATE INDEX idx_billing_client_vendor ON billing_runs(client_id, vendor_id);
CREATE INDEX idx_billing_month ON billing_runs(billing_month);

-- 7a. Billing month validation trigger
CREATE FUNCTION enforce_first_day_month()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
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
FOR EACH ROW EXECUTE FUNCTION enforce_first_day_month();

-- 8. TRIPS (Unified Ingestion Schema)
CREATE TABLE trips (
  trip_id SERIAL PRIMARY KEY,
  contract_id INT NOT NULL REFERENCES contracts(contract_id),
  client_id INT NOT NULL REFERENCES clients(client_id),
  vendor_id INT NOT NULL REFERENCES vendors(vendor_id),
  employee_id INT REFERENCES employees(employee_id),
  booking_time TIMESTAMPTZ,       -- Scheduled Time
  vehicle_type TEXT,              -- For Rate Checks
  vehicle_number TEXT,            -- For Audit
  trip_type trip_type_enum,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL,
  distance_km NUMERIC(10,2) NOT NULL,
  duration_min INT NOT NULL,
  currency TEXT DEFAULT 'INR',
  raw_data JSONB NOT NULL,
  ingested_at TIMESTAMPTZ DEFAULT NOW(),
  status trip_status_enum DEFAULT 'INGESTED',
  billing_run_id INT REFERENCES billing_runs(billing_run_id),
  CONSTRAINT chk_trip_time CHECK (end_time >= start_time)
);

CREATE INDEX idx_trips_contract ON trips(contract_id);
CREATE INDEX idx_trips_client ON trips(client_id);
CREATE INDEX idx_trips_vendor ON trips(vendor_id);
CREATE INDEX idx_trips_start ON trips(start_time);

-- Trips ↔ Contract validation
CREATE FUNCTION fn_check_trip_contract_match()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
  c_client INT;
  c_vendor INT;
BEGIN
  SELECT client_id, vendor_id INTO c_client, c_vendor
  FROM contracts WHERE contract_id = NEW.contract_id;

  IF c_client <> NEW.client_id OR c_vendor <> NEW.vendor_id THEN
    RAISE EXCEPTION 'Trip client/vendor do not match contract';
  END IF;

  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_check_trip_contract_match
BEFORE INSERT OR UPDATE ON trips
FOR EACH ROW EXECUTE FUNCTION fn_check_trip_contract_match();

-- 9. TRIP CHARGES (Final Output)
CREATE TABLE trip_charges (
  charge_id SERIAL PRIMARY KEY,
  trip_id INT NOT NULL REFERENCES trips(trip_id),
  billing_run_id INT NOT NULL REFERENCES billing_runs(billing_run_id),
  base_cost NUMERIC(12,2),
  extra_km NUMERIC(12,2),
  extra_km_cost NUMERIC(12,2),
  extra_hours NUMERIC(12,2),
  extra_hours_cost NUMERIC(12,2),
  incentive_amount NUMERIC(12,2),
  vendor_payout NUMERIC(12,2),
  final_cost NUMERIC(12,2) NOT NULL,
  formula_snapshot JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trip_charges_run ON trip_charges(billing_run_id);

-- 10. AUDIT LOGS
CREATE TABLE audit_logs (
  audit_id SERIAL PRIMARY KEY,
  entity TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  action audit_action_enum NOT NULL,
  snapshot JSONB NOT NULL,
  performed_by INT REFERENCES users(user_id),
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 11. SEED (Optional)
INSERT INTO clients (name) VALUES ('Google');
INSERT INTO vendors (name) VALUES ('SRS Travels');
INSERT INTO users (username, password_hash, role) VALUES ('admin', 'secret', 'ADMIN');

INSERT INTO contracts (client_id, vendor_id, model_type, config_json, start_date, end_date)
VALUES (1, 1, 'PACKAGE', '{"monthly_cost": 40000}', '2025-01-01', '2026-01-01');
