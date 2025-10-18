"""CFTS Database models."""
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from ..db.database import Base


class CFTSRequirementDB(Base):
    __tablename__ = "cfts_requirements"

    id = Column(Integer, primary_key=True, index=True)
    cfts_id = Column(String, index=True)
    cfts_name = Column(String, default="")  # CFTS名稱（從檔名提取，例如：Anti-Theft）
    req_id = Column(String, index=True)  # ReqIF.ForeignID（數字，可能重複）
    source_id = Column(String, index=True)  # Source Id（可能重複，因為對應多個Melco ID）
    description = Column(String, default="")  # SR26 Description
    sr24_description = Column(String, default="")  # SR24 Description
    melco_id = Column(String, default="")  # Melco ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())