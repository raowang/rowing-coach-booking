from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.directus import get_directus_client
from app.models import TrainingRecordCreate, TrainingRecordUpdate, TrainingRecordResponse
from app.services.feedback_service import feedback_service

router = APIRouter(prefix="/training-records", tags=["training-records"])
directus = get_directus_client()


@router.post("/", response_model=TrainingRecordResponse)
async def create_training_record(record: TrainingRecordCreate):
    result = await feedback_service.create_training_record(
        booking_id=record.booking_id,
        member_id=record.member_id,
        coach_id=record.coach_id,
        rating=record.rating,
        coach_comment=record.coach_comment
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create training record")
    return TrainingRecordResponse(**result)


@router.get("/{record_id}", response_model=TrainingRecordResponse)
async def get_training_record(record_id: str):
    result = await feedback_service.get_training_record(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Training record not found")
    return TrainingRecordResponse(**result)


@router.get("/", response_model=list[TrainingRecordResponse])
async def list_training_records(
    member_id: Optional[str] = None,
    coach_id: Optional[str] = None,
    booking_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    filter_conditions = []
    if member_id:
        filter_conditions.append({"member_id": {"_eq": member_id}})
    if coach_id:
        filter_conditions.append({"coach_id": {"_eq": coach_id}})
    if booking_id:
        filter_conditions.append({"booking_id": {"_eq": booking_id}})

    filter_cond = {"_and": filter_conditions} if filter_conditions else {}

    result = await directus.query(
        "training_records",
        filter=filter_cond if filter_cond else None,
        limit=limit,
        offset=offset
    )
    records = result.get("data", [])
    return [TrainingRecordResponse(**r) for r in records]


@router.patch("/{record_id}", response_model=TrainingRecordResponse)
async def update_training_record(record_id: str, record: TrainingRecordUpdate):
    update_data = {k: v for k, v in record.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await feedback_service.update_training_record(record_id, **update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Training record not found")
    return TrainingRecordResponse(**result)


@router.delete("/{record_id}")
async def delete_training_record(record_id: str):
    await directus.delete_item("training_records", record_id)
    return {"message": "Training record deleted successfully"}
