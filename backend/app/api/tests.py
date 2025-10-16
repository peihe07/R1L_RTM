"""Test cases API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models.testcase import TestCase

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("/", response_model=List[TestCase])
async def get_test_cases():
    """Get all test cases."""
    pass


@router.get("/{test_id}", response_model=TestCase)
async def get_test_case(test_id: int):
    """Get a specific test case."""
    pass


@router.post("/", response_model=TestCase)
async def create_test_case(test_case: TestCase):
    """Create a new test case."""
    pass


@router.put("/{test_id}", response_model=TestCase)
async def update_test_case(test_id: int, test_case: TestCase):
    """Update a test case."""
    pass


@router.delete("/{test_id}")
async def delete_test_case(test_id: int):
    """Delete a test case."""
    pass


@router.get("/requirement/{requirement_id}", response_model=List[TestCase])
async def get_test_cases_by_requirement(requirement_id: int):
    """Get all test cases for a specific requirement."""
    pass