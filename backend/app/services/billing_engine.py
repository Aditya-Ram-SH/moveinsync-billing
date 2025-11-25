from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import BillingRun, Contract, Trip, TripCharge
from app.services.audit import record_audit_log


class BillingEngine:
    def __init__(self, db: Session):
        self.db = db

    def run(
        self,
        *,
        client_id: int,
        vendor_id: int,
        billing_start: date,
        billing_end: date,
        triggered_by: int,
    ) -> BillingRun:
        # Check contract is active at billing_start
        contract = (
            self.db.query(Contract)
            .filter(
                Contract.client_id == client_id,
                Contract.vendor_id == vendor_id,
                Contract.is_active.is_(True),
                Contract.start_date <= billing_start,
                Contract.end_date >= billing_start,
            )
            .order_by(Contract.version.desc())
            .first()
        )
        if not contract:
            raise ValueError("No active contract found")

        # Check if billing run already exists
        run = (
            self.db.query(BillingRun)
            .filter(
                BillingRun.client_id == client_id,
                BillingRun.vendor_id == vendor_id,
                BillingRun.billing_start == billing_start,
            )
            .first()
        )

        # If run exists and is SUCCESS, return it without recalculating
        if run and run.status == "SUCCESS":
            return run

        # If run exists but is FAILED or RUNNING, recalculate
        if run:
            # Delete old charges
            self.db.execute(delete(TripCharge).where(TripCharge.billing_run_id == run.billing_run_id))
            run.status = "RUNNING"
            run.started_at = datetime.utcnow()
            run.completed_at = None
            run.notes = None
        else:
            # Create new run
            run = BillingRun(
                client_id=client_id,
                vendor_id=vendor_id,
                billing_start=billing_start,
                billing_end=billing_end,
                triggered_by=triggered_by,
                status="RUNNING",
            )
            self.db.add(run)
            self.db.flush()

        # Convert dates to datetime for trip query
        period_start = datetime.combine(billing_start, datetime.min.time())
        period_end = datetime.combine(billing_end, datetime.min.time())

        trips: List[Trip] = (
            self.db.query(Trip)
            .filter(
                Trip.client_id == client_id,
                Trip.vendor_id == vendor_id,
                Trip.status == "INGESTED",
                Trip.start_time >= period_start,
                Trip.start_time < period_end,
            )
            .order_by(Trip.start_time)
            .all()
        )

        if not trips:
            # No trips found - still create billing run but mark with note
            run.status = "SUCCESS"
            run.completed_at = datetime.utcnow()
            run.notes = f"No INGESTED trips found for client {client_id}, vendor {vendor_id} for period {billing_start.isoformat()} to {billing_end.isoformat()}"
            
            # Create audit log even with 0 trips
            record_audit_log(
                self.db,
                entity="BILLING_RUN",
                entity_id=str(run.billing_run_id),
                action="CREATE",
                snapshot={
                    "billing_run_id": run.billing_run_id,
                    "client_id": run.client_id,
                    "vendor_id": run.vendor_id,
                    "billing_start": run.billing_start.isoformat(),
                    "billing_end": run.billing_end.isoformat(),
                    "status": run.status,
                    "trips_processed": 0,
                    "total_vendor_payout": 0.0,
                    "total_final_cost": 0.0,
                    "notes": run.notes,
                    "warning": "No trips found matching criteria",
                },
                performed_by=triggered_by,
            )
            return run

        total_vendor_payout = Decimal("0")
        total_final = Decimal("0")
        charges: List[TripCharge] = []

        for trip in trips:
            breakdown = self._calculate_trip(trip, contract.config_json, contract.model_type)
            charge = TripCharge(
                trip_id=trip.trip_id,
                billing_run_id=run.billing_run_id,
                base_cost=breakdown["base_cost"],
                extra_km=breakdown["extra_km"],
                extra_km_cost=breakdown["extra_km_cost"],
                extra_hours=breakdown["extra_hours"],
                extra_hours_cost=breakdown["extra_hours_cost"],
                incentive_amount=breakdown["incentive_amount"],
                vendor_payout=breakdown["vendor_payout"],
                final_cost=breakdown["final_cost"],
                formula_snapshot=contract.config_json,
            )
            self.db.add(charge)
            charges.append(charge)

            trip.status = "PROCESSED"
            trip.billing_run_id = run.billing_run_id

            total_vendor_payout += breakdown["vendor_payout"]
            total_final += breakdown["final_cost"]

        notes: List[str] = []
        if contract.model_type == "HYBRID_A":
            guarantee = Decimal(str(contract.config_json.get("guarantee", {}).get("monthly_min_payout", 0)))
            if guarantee and total_vendor_payout < guarantee and charges:
                delta = guarantee - total_vendor_payout
                charges[0].vendor_payout = (charges[0].vendor_payout or Decimal("0")) + delta
                charges[0].final_cost = (charges[0].final_cost or Decimal("0")) + delta
                total_vendor_payout += delta
                total_final += delta
                notes.append(f"Guarantee adjustment applied (+{delta}).")

        if contract.model_type == "PACKAGE":
            fixed_pay = Decimal(str(contract.config_json.get("monthly_fixed_pay", 0)))
            if fixed_pay:
                total_final += fixed_pay
                notes.append(f"Includes fixed package fee of {fixed_pay}.")

        run.status = "SUCCESS"
        run.completed_at = datetime.utcnow()
        run.notes = " ".join(notes) if notes else None

        # Create audit log for billing run
        record_audit_log(
            self.db,
            entity="BILLING_RUN",
            entity_id=str(run.billing_run_id),
            action="CREATE",
            snapshot={
                "billing_run_id": run.billing_run_id,
                "client_id": run.client_id,
                "vendor_id": run.vendor_id,
                "billing_start": run.billing_start.isoformat(),
                "billing_end": run.billing_end.isoformat(),
                "status": run.status,
                "trips_processed": len(charges),
                "total_vendor_payout": float(total_vendor_payout),
                "total_final_cost": float(total_final),
                "notes": run.notes,
            },
            performed_by=triggered_by,
        )

        return run

    def _calculate_trip(
        self,
        trip: Trip,
        config: Dict,
        model_type: str,
    ) -> Dict[str, Decimal]:
        distance = Decimal(str(trip.distance_km))
        emp_incentive = self._compute_employee_incentive(trip, config)
        is_night = _is_night_trip(trip.start_time)

        payload = {
            "base_cost": Decimal("0"),
            "extra_km": Decimal("0"),
            "extra_km_cost": Decimal("0"),
            "extra_hours": Decimal("0"),
            "extra_hours_cost": Decimal("0"),
            "incentive_amount": emp_incentive,
            "vendor_payout": Decimal("0"),
        }

        if model_type == "PACKAGE":
            limits = config.get("limits", {})
            vendor_cfg = config.get("vendor_payouts", {})
            included_km_trip = Decimal(str(limits.get("included_km_per_trip", 0)))
            extra_km = max(distance - included_km_trip, Decimal("0"))
            payload["extra_km"] = extra_km
            payload["extra_km_cost"] = extra_km * Decimal(str(vendor_cfg.get("per_extra_km", 0)))

            extra_trip_bonus = Decimal(str(vendor_cfg.get("per_extra_trip", 0)))
            night_bonus = Decimal(str(vendor_cfg.get("night_shift_bonus", 0))) if is_night else Decimal("0")
            vendor_total = payload["extra_km_cost"] + extra_trip_bonus + night_bonus
            payload["vendor_payout"] = vendor_total

        elif model_type == "TRIP":
            rates = config.get("rates", {})
            base_fare = Decimal(str(rates.get("base_fare", 0)))
            per_km = Decimal(str(rates.get("per_km_rate", 0)))
            night_multiplier = Decimal(str(rates.get("night_multiplier", 1)))

            distance_cost = distance * per_km
            ride_cost = (base_fare + distance_cost) * (night_multiplier if is_night else Decimal("1"))
            payload["base_cost"] = base_fare
            payload["extra_km"] = distance
            payload["extra_km_cost"] = distance_cost
            payload["vendor_payout"] = ride_cost

        elif model_type == "HYBRID_A":
            rates = config.get("rates", {})
            base_fare = Decimal(str(rates.get("base_fare_per_trip", 0)))
            per_km_rate = Decimal(str(rates.get("per_km_rate", 0)))
            ride_cost = base_fare + (per_km_rate * distance)
            payload["base_cost"] = base_fare
            payload["extra_km"] = distance
            payload["extra_km_cost"] = per_km_rate * distance
            payload["vendor_payout"] = ride_cost

        elif model_type == "HYBRID_B":
            rates = config.get("rates", {})
            thresholds = config.get("thresholds", {})
            fixed_pay = Decimal(str(rates.get("fixed_base_pay", 0)))
            extra_rate = Decimal(str(rates.get("per_extra_km_rate", 0)))
            included = Decimal(str(thresholds.get("included_km_per_trip", 0)))
            extra_km = max(distance - included, Decimal("0"))
            payload["base_cost"] = fixed_pay
            payload["extra_km"] = extra_km
            payload["extra_km_cost"] = extra_km * extra_rate
            payload["vendor_payout"] = fixed_pay + payload["extra_km_cost"]

        payload["final_cost"] = payload["vendor_payout"] + emp_incentive
        return payload

    def _compute_employee_incentive(self, trip: Trip, config: Dict) -> Decimal:
        incentives = config.get("employee_incentives", {}) or {}
        threshold = Decimal(str(incentives.get("delay_threshold_min", 10)))
        amount = Decimal(str(incentives.get("delay_compensation_amount", 0)))
        if not trip.booking_time:
            return Decimal("0")
        delay = (trip.start_time - trip.booking_time).total_seconds() / 60
        if Decimal(str(delay)) > threshold:
            return amount
        return Decimal("0")


def _is_night_trip(start_time: datetime | None) -> bool:
    if not start_time:
        return False
    hour = start_time.hour
    return hour >= 22 or hour < 6

