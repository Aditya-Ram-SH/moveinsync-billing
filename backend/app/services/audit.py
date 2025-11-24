from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models import AuditLog


def record_audit_log(
    db: Session,
    *,
    entity: str,
    entity_id: str,
    action: str,
    snapshot: Dict[str, Any],
    performed_by: int | None,
) -> None:
    log = AuditLog(
        entity=entity,
        entity_id=entity_id,
        action=action,
        snapshot=snapshot,
        performed_by=performed_by,
    )
    db.add(log)

