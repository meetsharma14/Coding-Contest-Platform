# ==================================
# SHARED CRUD UTILITIES
#
# Reusable database helper functions
# used across multiple routers
# ==================================

from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_or_404(
    db: Session,
    model,
    entity_id: int,
    detail: str = "Not found"
):
    """Fetch a record by primary key or raise HTTP 404."""

    obj = (
        db.query(model)
        .filter(model.id == entity_id)
        .first()
    )

    if not obj:
        raise HTTPException(
            status_code=404,
            detail=detail
        )

    return obj


def save_and_refresh(db: Session, obj):
    """Add a new record, commit, and refresh to populate generated fields."""

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


def check_unique_or_400(
    db: Session,
    model,
    field,
    value,
    detail: str
):
    """Raise HTTP 400 if a record with the given field value already exists."""

    exists = (
        db.query(model)
        .filter(field == value)
        .first()
    )

    if exists:
        raise HTTPException(
            status_code=400,
            detail=detail
        )
