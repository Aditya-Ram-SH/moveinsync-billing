from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.templates import CONTRACT_TEMPLATES
from app.db.session import get_db
from app.models import Contract, User
from app.routers.deps import get_current_admin, get_current_user
from app.schemas import ContractCreate
from app.services.audit import record_audit_log

router = APIRouter()


@router.get("/templates")
def get_contract_templates(_: str = Depends(get_current_user)):
    """
    Returns the form structure for creating contracts.
    Frontend uses this to render dynamic forms based on model_type.
    """
    return CONTRACT_TEMPLATES


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
    
    return query.order_by(Contract.client_id, Contract.vendor_id, Contract.version.desc()).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_contract(
    payload: ContractCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    overlapping = (
        db.query(Contract)
        .filter(
            Contract.client_id == payload.client_id,
            Contract.vendor_id == payload.vendor_id,
            Contract.version == payload.version,
        )
        .first()
    )
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract version already exists for client/vendor",
        )

    contract = Contract(
        client_id=payload.client_id,
        vendor_id=payload.vendor_id,
        model_type=payload.model_type,
        config_json=payload.config_json,
        version=payload.version,
        start_date=payload.start_date,
        end_date=payload.end_date,
        is_active=payload.is_active,
        created_by=current_user.user_id,
    )
    db.add(contract)
    db.flush()

    record_audit_log(
        db,
        entity="contract",
        entity_id=str(contract.contract_id),
        action="CREATE",
        snapshot=payload.model_dump(),
        performed_by=current_user.user_id,
    )

    db.commit()
    db.refresh(contract)
    return contract


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

