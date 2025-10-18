"""CFTS Requirement model definition."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CFTSRequirement(BaseModel):
    cfts_id: str
    cfts_name: Optional[str] = None
    req_id: str
    polarian_id: Optional[str] = None
    polarian_url: Optional[str] = None
    description: Optional[str] = None
    spec_object_type: Optional[str] = None
    sys2_scope: Optional[str] = None
    melco_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CFTSSearchResult(BaseModel):
    cfts_id: str
    requirements: List[CFTSRequirement]
    total_count: int
    target_req_id: Optional[str] = None  # For Req.ID search, indicates which row to highlight

    class Config:
        from_attributes = True