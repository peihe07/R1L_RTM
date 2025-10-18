"""TestCase API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.testcase import TestCaseResponse
from ..db.database import get_db


router = APIRouter(prefix="/testcases", tags=["testcases"])


def db_testcase_to_response(db_tc) -> TestCaseResponse:
    """Convert database model to response Pydantic model."""
    return TestCaseResponse(
        feature_id=db_tc.feature_id,
        source=db_tc.source,
        title=db_tc.title,
        section=db_tc.section,
        test_item_en=db_tc.test_item_en,
        precondition_procedure_jp=db_tc.precondition_procedure_jp,
        criteria_jp=db_tc.criteria_jp
    )


@router.get("/by-feature-id/{feature_id}", response_model=List[TestCaseResponse])
async def get_testcases_by_feature_id(feature_id: str, db: Session = Depends(get_db)):
    """Get all TestCases for a specific Feature ID (Melco ID)."""
    from ..models.testcase import TestCaseDB

    db_testcases = db.query(TestCaseDB).filter(
        TestCaseDB.feature_id == feature_id
    ).all()

    if not db_testcases:
        # Return empty list instead of 404 for better UX
        return []

    return [db_testcase_to_response(tc) for tc in db_testcases]
