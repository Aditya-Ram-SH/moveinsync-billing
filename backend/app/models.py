from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    timezone = Column(String, default="UTC")
    status = Column(Enum("ACTIVE", "INACTIVE", name="status_enum"), default="ACTIVE")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_info = Column(Text)
    status = Column(Enum("ACTIVE", "INACTIVE", name="status_enum"), default="ACTIVE")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    full_name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum("ADMIN", "CLIENT", "VENDOR", "EMPLOYEE", name="role_enum"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"))
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = (
        UniqueConstraint("client_id", "vendor_id", "version", name="uniq_contract_version"),
    )

    contract_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=False)
    model_type = Column(
        Enum("PACKAGE", "TRIP", "HYBRID_A", "HYBRID_B", name="model_enum"),
        nullable=False,
    )
    config_json = Column(JSONB, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BillingRun(Base):
    __tablename__ = "billing_runs"
    __table_args__ = (
        UniqueConstraint("client_id", "vendor_id", "billing_start", name="uniq_billing_run"),
    )

    billing_run_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=False)
    billing_start = Column(Date, nullable=False)
    billing_end = Column(Date, nullable=False)
    triggered_by = Column(Integer, ForeignKey("users.user_id"))
    status = Column(
        Enum("RUNNING", "SUCCESS", "FAILED", name="billing_status_enum"),
        default="RUNNING",
    )
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    notes = Column(Text)


class Trip(Base):
    __tablename__ = "trips"

    trip_id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.contract_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    trip_type = Column(
        Enum("PICKUP", "DROPOFF", "INBOUND", "OUTBOUND", name="trip_type_enum"),
    )
    booking_time = Column(DateTime(timezone=True))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    distance_km = Column(Numeric(10, 2), nullable=False)
    duration_min = Column(Integer, nullable=False)
    vehicle_type = Column(String)
    vehicle_number = Column(String)
    currency = Column(String, default="INR")
    raw_data = Column(JSONB, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(
        Enum("INGESTED", "PROCESSED", "ERROR", name="trip_status_enum"),
        default="INGESTED",
    )
    billing_run_id = Column(Integer, ForeignKey("billing_runs.billing_run_id"))


class TripCharge(Base):
    __tablename__ = "trip_charges"

    charge_id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.trip_id"), nullable=False)
    billing_run_id = Column(Integer, ForeignKey("billing_runs.billing_run_id"), nullable=False)
    base_cost = Column(Numeric(12, 2))
    extra_km = Column(Numeric(12, 2))
    extra_km_cost = Column(Numeric(12, 2))
    extra_hours = Column(Numeric(12, 2))
    extra_hours_cost = Column(Numeric(12, 2))
    incentive_amount = Column(Numeric(12, 2))
    vendor_payout = Column(Numeric(12, 2))
    final_cost = Column(Numeric(12, 2), nullable=False)
    formula_snapshot = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id = Column(Integer, primary_key=True, index=True)
    entity = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    action = Column(Enum("CREATE", "UPDATE", "DELETE", name="audit_action_enum"), nullable=False)
    snapshot = Column(JSONB, nullable=False)
    performed_by = Column(Integer, ForeignKey("users.user_id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

