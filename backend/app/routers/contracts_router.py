from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.templates import CONTRACT_TEMPLATES
from app.db.session import get_db
from app.models import Contract, User
from app.routers.deps import get_current_admin, get_current_user
from app.schemas import ContractCreate, ContractCreateWithUsernames
from app.services.audit import record_audit_log
from app.utils.username_mapping import (
    get_client_id_from_username,
    get_vendor_id_from_username,
    get_username_from_client_id,
    get_username_from_vendor_id,
)

router = APIRouter()


@router.get("/templates")
def get_contract_templates(_: str = Depends(get_current_user)):
    """
    Returns the form structure for creating contracts.
    Frontend uses this to render dynamic forms based on model_type.
    """
    return CONTRACT_TEMPLATES


@router.get("")
@router.get("/")
def list_contracts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Contract)
    
    # Role-based filtering
    if current_user.role == "CLIENT":
        query = query.filter(Contract.client_id == current_user.client_id)
    elif current_user.role == "VENDOR":
        query = query.filter(Contract.vendor_id == current_user.vendor_id)
    elif current_user.role == "EMPLOYEE":
        # Employees don't see contracts
        return []
    # ADMIN sees all
    
    contracts = query.order_by(Contract.client_id, Contract.vendor_id, Contract.version.desc()).all()
    
    # Add usernames to response
    result = []
    for contract in contracts:
        contract_dict = {
            "contract_id": contract.contract_id,
            "client_id": contract.client_id,
            "vendor_id": contract.vendor_id,
            "client_username": get_username_from_client_id(db, contract.client_id) or f"Client #{contract.client_id}",
            "vendor_username": get_username_from_vendor_id(db, contract.vendor_id) or f"Vendor #{contract.vendor_id}",
            "model_type": contract.model_type,
            "config_json": contract.config_json,
            "version": contract.version,
            "start_date": contract.start_date.isoformat() if contract.start_date else None,
            "end_date": contract.end_date.isoformat() if contract.end_date else None,
            "is_active": contract.is_active,
            "created_by": contract.created_by,
            "created_at": contract.created_at.isoformat() if contract.created_at else None,
        }
        result.append(contract_dict)
    
    return result


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_contract(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    """Create contract - accepts usernames or IDs."""
    # Convert usernames to IDs if provided
    if "client_username" in payload:
        try:
            client_id = get_client_id_from_username(db, payload["client_username"])
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
    else:
        client_id = payload.get("client_id")
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either client_username or client_id is required",
            )
    
    if "vendor_username" in payload:
        try:
            vendor_id = get_vendor_id_from_username(db, payload["vendor_username"])
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
    else:
        vendor_id = payload.get("vendor_id")
        if not vendor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either vendor_username or vendor_id is required",
            )
    
    version = payload.get("version", 1)
    
    overlapping = (
        db.query(Contract)
        .filter(
            Contract.client_id == client_id,
            Contract.vendor_id == vendor_id,
            Contract.version == version,
        )
        .first()
    )
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract version already exists for client/vendor",
        )

    contract = Contract(
        client_id=client_id,
        vendor_id=vendor_id,
        model_type=payload["model_type"],
        config_json=payload["config_json"],
        version=version,
        start_date=payload["start_date"],
        end_date=payload["end_date"],
        is_active=payload.get("is_active", True),
        created_by=current_user.user_id,
    )
    db.add(contract)
    db.flush()

    record_audit_log(
        db,
        entity="contract",
        entity_id=str(contract.contract_id),
        action="CREATE",
        snapshot={
            "client_username": get_username_from_client_id(db, client_id),
            "vendor_username": get_username_from_vendor_id(db, vendor_id),
            "model_type": contract.model_type,
            "version": contract.version,
        },
        performed_by=current_user.user_id,
    )

    db.commit()
    db.refresh(contract)
    
    # Return with usernames
    return {
        "contract_id": contract.contract_id,
        "client_id": contract.client_id,
        "vendor_id": contract.vendor_id,
        "client_username": get_username_from_client_id(db, contract.client_id),
        "vendor_username": get_username_from_vendor_id(db, contract.vendor_id),
        "model_type": contract.model_type,
        "config_json": contract.config_json,
        "version": contract.version,
        "start_date": contract.start_date.isoformat() if contract.start_date else None,
        "end_date": contract.end_date.isoformat() if contract.end_date else None,
        "is_active": contract.is_active,
        "created_by": contract.created_by,
        "created_at": contract.created_at.isoformat() if contract.created_at else None,
    }


@router.get("/{contract_id}")
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    """Get a single contract by ID."""
    contract = db.query(Contract).filter(Contract.contract_id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    return contract

