"""SYS.2 Requirement models."""
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.sql import func
from ..db.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SYS2RequirementDB(Base):
    """SYS.2 Requirement database model."""
    __tablename__ = "sys2_requirements"

    id = Column(Integer, primary_key=True, index=True)
    melco_id = Column(String, index=True, unique=True)  # 要件ID (例: PSCFTS016-1-4-2)
    cfts_id = Column(String, index=True)  # CFTS編號 (例: CFTS016)
    cfts_name = Column(String, default="")  # CFTS名稱 (例: Anti-Theft)

    # 主要欄位
    requirement_en = Column(Text, default="")  # 要件(英語)
    reason_en = Column(Text, default="")  # 理由(英語)
    supplement_en = Column(Text, default="")  # 補足(英語)
    confirmation_phase = Column(String, default="")  # 確認フェーズ
    verification_criteria = Column(Text, default="")  # 検証基準

    # 其他欄位
    type = Column(String, default="")  # 種別
    related_requirement_ids = Column(Text, default="")  # 関連要件ID
    r1l_sr21cfts = Column(String, default="")  # (R1L_SR21CFTS)
    r1l_sr22cfts = Column(String, default="")  # (R1L_SR22CFTS)
    r1l_sr23cfts = Column(String, default="")  # (R1L_SR23CFTS)
    r1l_sr24cfts = Column(String, default="")  # (R1L_SR24CFTS)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SYS2Requirement(BaseModel):
    """SYS.2 Requirement Pydantic model."""
    melco_id: str
    cfts_id: str
    cfts_name: Optional[str] = ""
    requirement_en: Optional[str] = ""
    reason_en: Optional[str] = ""
    supplement_en: Optional[str] = ""
    confirmation_phase: Optional[str] = ""
    verification_criteria: Optional[str] = ""
    type: Optional[str] = ""
    related_requirement_ids: Optional[str] = ""
    r1l_sr21cfts: Optional[str] = ""
    r1l_sr22cfts: Optional[str] = ""
    r1l_sr23cfts: Optional[str] = ""
    r1l_sr24cfts: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SYS2RequirementDetail(BaseModel):
    """Detailed response for Melco ID query."""
    melco_id: str
    cfts_id: str
    cfts_name: str
    requirement_en: str
    reason_en: str
    supplement_en: str
    confirmation_phase: str
    verification_criteria: str
    type: str
    related_requirement_ids: str

    class Config:
        from_attributes = True
