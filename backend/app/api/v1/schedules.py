from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.directus import get_directus_client
from app.models import (
    CoachScheduleCreate,
    CoachScheduleUpdate,
    CoachScheduleResponse,
    CoachScheduleWithCoach,
)

router = APIRouter(prefix="/schedules", tags=["schedules"])
directus = get_directus_client()


@router.post("/", response_model=CoachScheduleResponse)
async def create_schedule(schedule: CoachScheduleCreate):
    schedule_data = schedule.model_dump()
    schedule_data["date"] = schedule_data["date"].isoformat()
    schedule_data["start_time"] = schedule_data["start_time"].isoformat()
    schedule_data["end_time"] = schedule_data["end_time"].isoformat()

    result = await directus.create_item("coach_schedules", schedule_data)
    data = result.get("data", {})
    return CoachScheduleResponse(**data)


@router.get("/{schedule_id}", response_model=CoachScheduleResponse)
async def get_schedule(schedule_id: str):
    result = await directus.get_item("coach_schedules", schedule_id)
    data = result.get("data")
    if not data:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return CoachScheduleResponse(**data)


@router.get("/", response_model=list[CoachScheduleWithCoach])
async def list_schedules(
    coach_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    is_available: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    filter_conditions = []
    if coach_id:
        filter_conditions.append({"coach_id": {"_eq": coach_id}})
    if is_available is not None:
        filter_conditions.append({"is_available": {"_eq": is_available}})
    if date_from:
        filter_conditions.append({"date": {"_gte": date_from.isoformat()}})
    if date_to:
        filter_conditions.append({"date": {"_lte": date_to.isoformat()}})

    filter_cond = {"_and": filter_conditions} if filter_conditions else {}

    result = await directus.query(
        "coach_schedules",
        filter=filter_cond if filter_cond else None,
        limit=limit,
        offset=offset
    )
    schedules = result.get("data", [])

    enriched_schedules = []
    for schedule in schedules:
        enriched = await _enrich_schedule(schedule)
        enriched_schedules.append(CoachScheduleWithCoach(**enriched))

    return enriched_schedules


@router.patch("/{schedule_id}", response_model=CoachScheduleResponse)
async def update_schedule(schedule_id: str, schedule: CoachScheduleUpdate):
    update_data = {}
    for k, v in schedule.model_dump().items():
        if v is not None:
            if k in ["date"]:
                update_data[k] = v.isoformat()
            elif k in ["start_time", "end_time"]:
                update_data[k] = v.isoformat()
            else:
                update_data[k] = v

    result = await directus.update_item("coach_schedules", schedule_id, update_data)
    data = result.get("data")
    if not data:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return CoachScheduleResponse(**data)


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str):
    await directus.delete_item("coach_schedules", schedule_id)
    return {"message": "Schedule deleted successfully"}


async def _enrich_schedule(schedule: dict) -> dict:
    enriched = dict(schedule)

    if schedule.get("coach_id"):
        try:
            coach_result = await directus.get_item("coaches", schedule["coach_id"])
            coach_data = coach_result.get("data", {})
            enriched["coach_name"] = coach_data.get("name")
        except Exception:
            enriched["coach_name"] = None

    return enriched
