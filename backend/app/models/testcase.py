"""Test case model definition."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class TestCaseStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TestCasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestCase(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    steps: str
    expected_result: str
    actual_result: Optional[str] = None
    status: TestCaseStatus = TestCaseStatus.DRAFT
    priority: TestCasePriority = TestCasePriority.MEDIUM
    requirement_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    executed_by: Optional[str] = None
    execution_date: Optional[datetime] = None
    tags: Optional[list[str]] = []

    class Config:
        from_attributes = True