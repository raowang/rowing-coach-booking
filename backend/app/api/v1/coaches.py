from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.directus import get_directus_client
from app.models import (
    CoachCreate,
    CoachUpdate,
    CoachResponse,
)

router = APIRouter(prefix="/coaches", tags=["coaches"])
directus = get_directus_client()


@router.post("/", response_model=CoachResponse)
async def create_coach(coach: CoachCreate):
    result = await directus.create_item("coaches", coach.model_dump())
    data = result.get("data", {})
    return CoachResponse(**data)


@router.get("/{coach_id}", response_model=CoachResponse)
async def get_coach(coach_id: str):
    result = await directus.get_item("coaches", coach_id)
    data = result.get("data")
    if not data:
        raise HTTPException(status_code=404, detail="Coach not found")
    return CoachResponse(**data)


@router.get("/", response_model=list[CoachResponse])
async def list_coaches(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    is_active: Optional[bool] = None,
    teaching_style: Optional[str] = None,
    specialty: Optional[str] = None
):
    filter_conditions = []
    if is_active is not None:
        filter_conditions.append({"is_active": {"_eq": is_active}})
    if teaching_style:
        filter_conditions.append({"teaching_style": {"_eq": teaching_style}})

    filter_cond = {"_and": filter_conditions} if filter_conditions else {}

    result = await directus.query(
        "coaches",
        filter=filter_cond if filter_cond else None,
        limit=limit,
        offset=offset
    )
    coaches = result.get("data", [])

    if specialty:
        coaches = [c for c in coaches if specialty in c.get("specialties", [])]

    return [CoachResponse(**c) for c in coaches]


@router.patch("/{coach_id}", response_model=CoachResponse)
async def update_coach(coach_id: str, coach: CoachUpdate):
    update_data = {k: v for k, v in coach.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await directus.update_item("coaches", coach_id, update_data)
    data = result.get("data")
    if not data:
        raise HTTPException(status_code=404, detail="Coach not found")
    return CoachResponse(**data)


@router.delete("/{coach_id}")
async def delete_coach(coach_id: str):
    await directus.delete_item("coaches", coach_id)
    return {"message": "Coach deleted successfully"}
