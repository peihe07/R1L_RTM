"""TestCase models."""
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.sql import func
from ..db.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TestCaseDB(Base):
    """TestCase database model."""
    __tablename__ = "testcases"

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(String, index=True)  # G欄: Feature-ID (對應Melco ID)

    # A-F欄位
    source = Column(String, default="")  # A欄: Source
    title = Column(String, default="")  # B欄: Title
    section = Column(String, default="")  # C欄: Section
    test_item_en = Column(Text, default="")  # D欄: TestItem(EN)
    precondition_procedure_jp = Column(Text, default="")  # E欄: Precondition/Procedure(JP)
    criteria_jp = Column(Text, default="")  # F欄: Criteria(JP)

    # 其他欄位（可選）
    mp = Column(String, default="")  # H欄: MP
    ds = Column(String, default="")  # I欄: DS
    dt = Column(String, default="")  # J欄: DT
    hdcc = Column(String, default="")  # K欄: HDCC
    ru = Column(String, default="")  # L欄: RU
    specification = Column(String, default="")  # M欄: Specification
    priority = Column(String, default="")  # N欄: Priority
    test_version = Column(String, default="")  # O欄: Test Version
    test_result = Column(String, default="")  # P欄: Test Result
    tester = Column(String, default="")  # Q欄: Tester
    issue_id = Column(String, default="")  # R欄: Issue ID
    note = Column(Text, default="")  # S欄: Note

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TestCase(BaseModel):
    """TestCase Pydantic model."""
    feature_id: str
    source: Optional[str] = ""
    title: Optional[str] = ""
    section: Optional[str] = ""
    test_item_en: Optional[str] = ""
    precondition_procedure_jp: Optional[str] = ""
    criteria_jp: Optional[str] = ""
    mp: Optional[str] = ""
    ds: Optional[str] = ""
    dt: Optional[str] = ""
    hdcc: Optional[str] = ""
    ru: Optional[str] = ""
    specification: Optional[str] = ""
    priority: Optional[str] = ""
    test_version: Optional[str] = ""
    test_result: Optional[str] = ""
    tester: Optional[str] = ""
    issue_id: Optional[str] = ""
    note: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestCaseResponse(BaseModel):
    """TestCase response for API."""
    feature_id: str
    source: str
    title: str
    section: str
    test_item_en: str
    precondition_procedure_jp: str
    criteria_jp: str

    class Config:
        from_attributes = True
