-- 1. ENUMS (Keep these, they are great)
CREATE TYPE role_enum AS ENUM ('ADMIN','CLIENT','VENDOR','EMPLOYEE');
CREATE TYPE status_enum AS ENUM ('ACTIVE','INACTIVE');
CREATE TYPE model_enum AS ENUM ('PACKAGE','TRIP','HYBRID');
CREATE TYPE trip_status_enum AS ENUM ('INGESTED','PROCESSED','ERROR');
CREATE TYPE trip_type_enum AS ENUM ('PICKUP','DROPOFF','INBOUND','OUTBOUND');
CREATE TYPE billing_status_enum AS ENUM ('RUNNING','SUCCESS','FAILED');
CREATE TYPE audit_entity_enum AS ENUM ('CONTRACT','BILLING_RUN');
CREATE TYPE audit_action_enum AS ENUM ('CREATE','UPDATE','DELETE');

-- 2. CLIENTS
CREATE TABLE clients (
  client_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  timezone TEXT DEFAULT 'UTC',
  status status_enum DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. VENDORS
CREATE TABLE vendors (
  vendor_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  contact_info TEXT,
  status status_enum DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. EMPLOYEES
CREATE TABLE employees (
  employee_id SERIAL PRIMARY KEY,
  client_id INT REFERENCES clients(client_id),
  full_name TEXT,
  email TEXT,
  phone TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. USERS
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role role_enum NOT NULL,
  client_id INT REFERENCES clients(client_id),
  vendor_id INT REFERENCES vendors(vendor_id),
  employee_id INT REFERENCES employees(employee_id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. CONTRACTS (Versioned & Configurable)
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

-- 7. BILLING RUNS
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

-- Trigger: Force 1st of month
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
  FOR EACH ROW EXECUTE FUNCTION enforce_first_day_month();

-- 8. TRIPS (Standard Table - No Partitioning)
CREATE TABLE trips (
  trip_id SERIAL PRIMARY KEY, -- Standard PK is back!
  contract_id INT NOT NULL REFERENCES contracts(contract_id),
  client_id INT NOT NULL REFERENCES clients(client_id),
  vendor_id INT NOT NULL REFERENCES vendors(vendor_id),
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
  billing_run_id INT REFERENCES billing_runs(billing_run_id),
  CONSTRAINT chk_trip_time CHECK (end_time >= start_time)
);

-- 9. TRIP CHARGES (Standard Table)
CREATE TABLE trip_charges (
  charge_id SERIAL PRIMARY KEY, -- Standard PK is back!
  trip_id INT NOT NULL REFERENCES trips(trip_id), -- Strict FK is back!
  billing_run_id INT NOT NULL REFERENCES billing_runs(billing_run_id),
  base_cost NUMERIC(10,2),
  extra_km NUMERIC(10,2),
  extra_km_cost NUMERIC(10,2),
  extra_hours NUMERIC(10,2),
  extra_hours_cost NUMERIC(10,2),
  final_cost NUMERIC(10,2) NOT NULL,
  formula_snapshot JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. AUDIT LOGS
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

-- 11. DATA INTEGRITY TRIGGER
CREATE FUNCTION fn_check_trip_contract_match() RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
  c_client INT;
  c_vendor INT;
BEGIN
  SELECT client_id, vendor_id INTO c_client, c_vendor FROM contracts WHERE contract_id = NEW.contract_id;
  IF c_client <> NEW.client_id OR c_vendor <> NEW.vendor_id THEN
    RAISE EXCEPTION 'Mismatch: Trip client/vendor does not match Contract';
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_check_trip_contract_match
  BEFORE INSERT OR UPDATE ON trips
  FOR EACH ROW EXECUTE FUNCTION fn_check_trip_contract_match();

-- 12. SEED DATA
INSERT INTO clients (name) VALUES ('Google');
INSERT INTO vendors (name) VALUES ('SRS Travels');
INSERT INTO users (username, password_hash, role) VALUES ('admin', 'secret', 'ADMIN');

INSERT INTO contracts (client_id, vendor_id, model_type, config_json, start_date, end_date)
VALUES (1, 1, 'PACKAGE', '{"monthly_cost": 40000}', '2025-01-01', '2026-01-01');

-- Performance Indexes (Run this in Adminer)
CREATE INDEX idx_trips_start_time ON trips(start_time);
CREATE INDEX idx_trip_charges_run ON trip_charges(billing_run_id);
CREATE INDEX idx_employees_client ON employees(client_id);