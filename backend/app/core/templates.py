"""
Contract templates for server-driven UI.
Defines the form structure for each billing model.
"""

CONTRACT_TEMPLATES = {
    "PACKAGE": {
        "label": "Corporate Fleet (Package Model)",
        "description": "Fixed monthly payment with overage limits and performance bonuses.",
        "sections": [
            {
                "title": "Base Payment",
                "fields": [
                    {
                        "key": "monthly_fixed_pay",
                        "label": "Monthly Fixed Pay (₹)",
                        "type": "number",
                        "required": True,
                        "default": 50000.00,
                        "help": "Fixed amount paid to vendor each month"
                    },
                    {
                        "key": "billing_cycle_months",
                        "label": "Billing Cycle (Months)",
                        "type": "number",
                        "required": True,
                        "default": 1
                    }
                ]
            },
            {
                "title": "Included Limits",
                "fields": [
                    {
                        "key": "limits.included_km",
                        "label": "Included Kilometers",
                        "type": "number",
                        "required": True,
                        "default": 5000,
                        "help": "Total KM included in fixed fee"
                    },
                    {
                        "key": "limits.included_trips",
                        "label": "Included Trips",
                        "type": "number",
                        "required": True,
                        "default": 500,
                        "help": "Total trips included in fixed fee"
                    }
                ]
            },
            {
                "title": "Vendor Performance Pay (Overage)",
                "fields": [
                    {
                        "key": "vendor_payouts.per_extra_km",
                        "label": "Rate per Extra KM (₹)",
                        "type": "number",
                        "required": True,
                        "default": 15.00,
                        "help": "Paid when exceeding included KM"
                    },
                    {
                        "key": "vendor_payouts.per_extra_trip",
                        "label": "Rate per Extra Trip (₹)",
                        "type": "number",
                        "required": True,
                        "default": 200.00,
                        "help": "Paid when exceeding included trips"
                    },
                    {
                        "key": "vendor_payouts.night_shift_bonus",
                        "label": "Night Shift Bonus (₹)",
                        "type": "number",
                        "required": True,
                        "default": 100.00,
                        "help": "Bonus per trip during night hours (10 PM - 6 AM)"
                    }
                ]
            },
            {
                "title": "Employee Incentives",
                "fields": [
                    {
                        "key": "employee_incentives.delay_threshold_min",
                        "label": "Delay Threshold (Minutes)",
                        "type": "number",
                        "required": True,
                        "default": 15,
                        "help": "Delay beyond this triggers compensation"
                    },
                    {
                        "key": "employee_incentives.delay_compensation_amount",
                        "label": "Compensation Amount (₹)",
                        "type": "number",
                        "required": True,
                        "default": 50.00,
                        "help": "Amount paid to employee for delays"
                    }
                ]
            }
        ]
    },
    
    "TRIP": {
        "label": "On-Demand (Trip Model)",
        "description": "Pay per use based on distance and time, like Uber/Ola.",
        "sections": [
            {
                "title": "Standard Rates",
                "fields": [
                    {
                        "key": "rates.base_fare",
                        "label": "Base Fare (₹)",
                        "type": "number",
                        "required": True,
                        "default": 100.00,
                        "help": "Minimum charge per trip"
                    },
                    {
                        "key": "rates.per_km_rate",
                        "label": "Rate per KM (₹)",
                        "type": "number",
                        "required": True,
                        "default": 12.00,
                        "help": "Charged for each kilometer traveled"
                    },
                    {
                        "key": "rates.night_multiplier",
                        "label": "Night Multiplier",
                        "type": "number",
                        "required": True,
                        "default": 1.5,
                        "help": "Multiply total fare by this during night (10 PM - 6 AM)"
                    }
                ]
            },
            {
                "title": "Billing Cycle",
                "fields": [
                    {
                        "key": "billing_cycle_months",
                        "label": "Billing Cycle (Months)",
                        "type": "number",
                        "required": True,
                        "default": 1
                    }
                ]
            },
            {
                "title": "Employee Incentives",
                "fields": [
                    {
                        "key": "employee_incentives.delay_threshold_min",
                        "label": "Delay Threshold (Minutes)",
                        "type": "number",
                        "required": True,
                        "default": 10,
                        "help": "Stricter SLA for on-demand service"
                    },
                    {
                        "key": "employee_incentives.delay_compensation_amount",
                        "label": "Compensation Amount (₹)",
                        "type": "number",
                        "required": True,
                        "default": 30.00
                    }
                ]
            }
        ]
    },
    
    "HYBRID_A": {
        "label": "Hybrid A (Minimum Guarantee)",
        "description": "Pay per trip with a guaranteed minimum monthly payout to vendor.",
        "sections": [
            {
                "title": "Per-Trip Rates",
                "fields": [
                    {
                        "key": "rates.base_fare_per_trip",
                        "label": "Base Fare per Trip (₹)",
                        "type": "number",
                        "required": True,
                        "default": 50.00
                    },
                    {
                        "key": "rates.per_km_rate",
                        "label": "Rate per KM (₹)",
                        "type": "number",
                        "required": True,
                        "default": 14.00
                    }
                ]
            },
            {
                "title": "Minimum Guarantee",
                "fields": [
                    {
                        "key": "guarantee.monthly_min_payout",
                        "label": "Monthly Minimum Payout (₹)",
                        "type": "number",
                        "required": True,
                        "default": 30000.00,
                        "help": "Vendor gets at least this amount even if trips are low"
                    }
                ]
            },
            {
                "title": "Billing Cycle",
                "fields": [
                    {
                        "key": "billing_cycle_months",
                        "label": "Billing Cycle (Months)",
                        "type": "number",
                        "required": True,
                        "default": 1
                    }
                ]
            },
            {
                "title": "Employee Incentives",
                "fields": [
                    {
                        "key": "employee_incentives.delay_threshold_min",
                        "label": "Delay Threshold (Minutes)",
                        "type": "number",
                        "required": True,
                        "default": 20
                    },
                    {
                        "key": "employee_incentives.delay_compensation_amount",
                        "label": "Compensation Amount (₹)",
                        "type": "number",
                        "required": True,
                        "default": 50.00
                    }
                ]
            }
        ]
    },
    
    "HYBRID_B": {
        "label": "Hybrid B (Base Distance Tier)",
        "description": "Fixed price per trip up to X km, then variable rate for extra distance.",
        "sections": [
            {
                "title": "Base Tier Rates",
                "fields": [
                    {
                        "key": "rates.fixed_base_pay",
                        "label": "Fixed Base Pay per Trip (₹)",
                        "type": "number",
                        "required": True,
                        "default": 300.00,
                        "help": "Flat rate for trips within included distance"
                    },
                    {
                        "key": "rates.per_extra_km_rate",
                        "label": "Rate per Extra KM (₹)",
                        "type": "number",
                        "required": True,
                        "default": 18.00,
                        "help": "Charged for distance beyond included KM"
                    }
                ]
            },
            {
                "title": "Distance Thresholds",
                "fields": [
                    {
                        "key": "thresholds.included_km_per_trip",
                        "label": "Included KM per Trip",
                        "type": "number",
                        "required": True,
                        "default": 15.0,
                        "help": "Distance included in fixed base pay"
                    }
                ]
            },
            {
                "title": "Billing Cycle",
                "fields": [
                    {
                        "key": "billing_cycle_months",
                        "label": "Billing Cycle (Months)",
                        "type": "number",
                        "required": True,
                        "default": 1
                    }
                ]
            },
            {
                "title": "Employee Incentives",
                "fields": [
                    {
                        "key": "employee_incentives.delay_threshold_min",
                        "label": "Delay Threshold (Minutes)",
                        "type": "number",
                        "required": True,
                        "default": 15
                    },
                    {
                        "key": "employee_incentives.delay_compensation_amount",
                        "label": "Compensation Amount (₹)",
                        "type": "number",
                        "required": True,
                        "default": 40.00
                    }
                ]
            }
        ]
    }
}

