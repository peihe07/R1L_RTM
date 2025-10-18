"""CFTS Database models."""
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from ..db.database import Base


class CFTSRequirementDB(Base):
    __tablename__ = "cfts_requirements"

    id = Column(Integer, primary_key=True, index=True)
    cfts_id = Column(String, index=True)
    cfts_name = Column(String, default="")  # CFTS名稱（從檔名提取，例如：Anti-Theft）
    req_id = Column(String, index=True)  # C欄：ReqIF.ForeignID（數字，可能重複）
    polarian_id = Column(String, index=True, unique=True)  # A欄：ID（NEWR1L-xxxxx，唯一）
    polarian_url = Column(String, default="")  # A欄：Polarion 超連結
    description = Column(String, default="")
    spec_object_type = Column(String, default="")
    sys2_scope = Column(String, default="")  # SYS2 I欄：SW/HW/System
    melco_id = Column(String, default="")  # SYS2 B欄：Melco ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())