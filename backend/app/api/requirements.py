"""CFTS Requirements API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.requirement import CFTSRequirement, CFTSSearchResult
from ..db.database import get_db
from ..db.crud import (
    get_cfts_requirements_by_cfts_id, 
    get_requirement_by_req_id,
    get_all_cfts_requirements
)

router = APIRouter(prefix="/cfts", tags=["cfts"])
req_router = APIRouter(prefix="/req", tags=["req"])


def db_requirement_to_pydantic(db_req) -> CFTSRequirement:
    """Convert database model to Pydantic model."""
    return CFTSRequirement(
        cfts_id=db_req.cfts_id,
        req_id=db_req.req_id,
        polarian_id=db_req.polarian_id,
        polarian_url=db_req.polarian_url,
        description=db_req.description,
        spec_object_type=db_req.spec_object_type,
        sys2_scope=db_req.sys2_scope,
        melco_id=db_req.melco_id,
        created_at=db_req.created_at,
        updated_at=db_req.updated_at
    )


@router.get("/search", response_model=CFTSSearchResult)
async def search_cfts(cfts_id: str = Query(..., description="CFTS ID to search (supports partial matching, e.g., 'CFTS016')"), db: Session = Depends(get_db)):
    """Search requirements by CFTS ID (supports partial matching)."""
    db_requirements = get_cfts_requirements_by_cfts_id(db, cfts_id)
    
    if not db_requirements:
        raise HTTPException(status_code=404, detail="CFTS not found")
    
    requirements = [db_requirement_to_pydantic(req) for req in db_requirements]
    
    return CFTSSearchResult(
        cfts_id=cfts_id,
        requirements=requirements,
        total_count=len(requirements)
    )


@req_router.get("/search", response_model=CFTSSearchResult)
async def search_req(req_id: str = Query(..., description="Req.ID to search"), db: Session = Depends(get_db)):
    """Search requirement by Req.ID and return full CFTS list."""
    db_requirement = get_requirement_by_req_id(db, req_id)

    if not db_requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    # Get all requirements from the same CFTS
    cfts_id = db_requirement.cfts_id
    db_requirements = get_cfts_requirements_by_cfts_id(db, cfts_id)

    requirements = [db_requirement_to_pydantic(req) for req in db_requirements]

    return CFTSSearchResult(
        cfts_id=cfts_id,
        requirements=requirements,
        total_count=len(requirements),
        target_req_id=req_id  # Add target req_id for highlighting
    )


@router.get("/requirement/{req_id}", response_model=CFTSRequirement)
async def get_requirement_by_id(req_id: str, db: Session = Depends(get_db)):
    """Get specific requirement by Req.ID."""
    db_requirement = get_requirement_by_req_id(db, req_id)
    
    if not db_requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    return db_requirement_to_pydantic(db_requirement)


@router.get("/", response_model=List[CFTSRequirement])
async def get_all_requirements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all CFTS requirements."""
    db_requirements = get_all_cfts_requirements(db, skip=skip, limit=limit)
    return [db_requirement_to_pydantic(req) for req in db_requirements]


@router.get("/autocomplete/cfts-ids")
async def autocomplete_cfts_ids(db: Session = Depends(get_db)):
    """Get unique CFTS IDs for autocomplete."""
    from sqlalchemy import distinct
    from ..models.cfts_db import CFTSRequirementDB

    cfts_ids = db.query(distinct(CFTSRequirementDB.cfts_id)).order_by(CFTSRequirementDB.cfts_id).all()
    return [cfts_id[0] for cfts_id in cfts_ids if cfts_id[0]]


@req_router.get("/autocomplete/req-ids")
async def autocomplete_req_ids(query: str = Query("", min_length=0), db: Session = Depends(get_db)):
    """Get Req IDs for autocomplete (with optional prefix filter)."""
    from ..models.cfts_db import CFTSRequirementDB

    req_query = db.query(CFTSRequirementDB.req_id).order_by(CFTSRequirementDB.req_id)

    if query:
        req_query = req_query.filter(CFTSRequirementDB.req_id.like(f"{query}%"))

    req_ids = req_query.limit(100).all()
    return [req_id[0] for req_id in req_ids if req_id[0]]