"""SYS.2 Requirements API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from ..models.sys2_requirement import SYS2RequirementDetail
from ..models.cfts_db import CFTSRequirementDB
from ..db.database import get_db


router = APIRouter(prefix="/sys2", tags=["sys2"])


def db_sys2_to_detail(db_req) -> SYS2RequirementDetail:
    """Convert database model to detail Pydantic model."""
    return SYS2RequirementDetail(
        melco_id=db_req.melco_id,
        cfts_id=db_req.cfts_id,
        cfts_name=db_req.cfts_name,
        requirement_en=db_req.requirement_en,
        reason_en=db_req.reason_en,
        supplement_en=db_req.supplement_en,
        confirmation_phase=db_req.confirmation_phase,
        verification_criteria=db_req.verification_criteria,
        type=db_req.type,
        related_requirement_ids=db_req.related_requirement_ids
    )


@router.get("/requirement/{melco_id}", response_model=List[SYS2RequirementDetail])
async def get_sys2_requirement(melco_id: str, db: Session = Depends(get_db)):
    """Get SYS.2 requirement details by Melco ID."""
    from ..models.sys2_requirement import SYS2RequirementDB

    db_requirements = db.query(SYS2RequirementDB).filter(
        SYS2RequirementDB.melco_id == melco_id
    ).all()

    if not db_requirements:
        raise HTTPException(status_code=404, detail=f"Melco ID {melco_id} not found")

    return [db_sys2_to_detail(req) for req in db_requirements]


@router.get("/by-cfts/{cfts_id}", response_model=List[SYS2RequirementDetail])
async def get_sys2_by_cfts(cfts_id: str, db: Session = Depends(get_db)):
    """Get all SYS.2 requirements for a specific CFTS."""
    from ..models.sys2_requirement import SYS2RequirementDB

    db_requirements = db.query(SYS2RequirementDB).filter(
        SYS2RequirementDB.cfts_id == cfts_id
    ).all()

    if not db_requirements:
        raise HTTPException(status_code=404, detail=f"No SYS.2 requirements found for CFTS {cfts_id}")

    return [db_sys2_to_detail(req) for req in db_requirements]
