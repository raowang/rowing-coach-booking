from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.directus import get_directus_client
from app.models import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingWithDetails,
    BookingStatus,
)
from app.services.scheduling_service import scheduling_service

router = APIRouter(prefix="/bookings", tags=["bookings"])
directus = get_directus_client()


@router.post("/", response_model=BookingResponse)
async def create_booking(booking: BookingCreate):
    result = await scheduling_service.create_booking(
        member_id=booking.member_id,
        coach_id=booking.coach_id,
        scheduled_time=booking.scheduled_time,
        end_time=booking.end_time
    )
    if not result:
        raise HTTPException(status_code=409, detail="Time slot not available or conflict")
    return BookingResponse(**result)


@router.get("/{booking_id}", response_model=BookingWithDetails)
async def get_booking(booking_id: str):
    result = await directus.get_item("bookings", booking_id)
    data = result.get("data")
    if not data:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking_with_details = await _enrich_booking(data)
    return BookingWithDetails(**booking_with_details)


@router.get("/", response_model=list[BookingWithDetails])
async def list_bookings(
    member_id: Optional[str] = None,
    coach_id: Optional[str] = None,
    status: Optional[BookingStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    filter_conditions = []
    if member_id:
        filter_conditions.append({"member_id": {"_eq": member_id}})
    if coach_id:
        filter_conditions.append({"coach_id": {"_eq": coach_id}})
    if status:
        filter_conditions.append({"status": {"_eq": status.value}})

    filter_cond = {"_and": filter_conditions} if filter_conditions else {}

    result = await directus.query(
        "bookings",
        filter=filter_cond if filter_cond else None,
        limit=limit,
        offset=offset
    )
    bookings = result.get("data", [])

    enriched_bookings = []
    for booking in bookings:
        enriched = await _enrich_booking(booking)
        enriched_bookings.append(BookingWithDetails(**enriched))

    return enriched_bookings


@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: str, booking: BookingUpdate):
    booking_data = await scheduling_service.get_booking(booking_id)
    if not booking_data:
        raise HTTPException(status_code=404, detail="Booking not found")

    update_data = {k: v for k, v in booking.model_dump().items() if v is not None}

    if booking.status:
        if booking.status == BookingStatus.CONFIRMED:
            result = await scheduling_service.confirm_booking(booking_id)
        elif booking.status == BookingStatus.CANCELLED:
            result = await scheduling_service.cancel_booking(booking_id)
        elif booking.status == BookingStatus.IN_PROGRESS:
            result = await scheduling_service.start_training(booking_id)
        elif booking.status == BookingStatus.COMPLETED:
            result = await scheduling_service.complete_training(booking_id)
        else:
            result = await directus.update_item("bookings", booking_id, update_data)
    else:
        result = await directus.update_item("bookings", booking_id, update_data)

    data = result.get("data") if result else None
    if not data:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingResponse(**data)


@router.post("/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(booking_id: str):
    result = await scheduling_service.confirm_booking(booking_id)
    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingResponse(**result)


@router.post("/{booking_id}/reject")
async def reject_booking(booking_id: str, reason: Optional[str] = None):
    result = await scheduling_service.reject_booking(booking_id, reason)
    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking rejected"}


@router.post("/{booking_id}/cancel")
async def cancel_booking(booking_id: str):
    result = await scheduling_service.cancel_booking(booking_id)
    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking cancelled"}


@router.post("/{booking_id}/start", response_model=BookingResponse)
async def start_training(booking_id: str):
    result = await scheduling_service.start_training(booking_id)
    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingResponse(**result)


@router.post("/{booking_id}/complete", response_model=BookingResponse)
async def complete_training(booking_id: str):
    result = await scheduling_service.complete_training(booking_id)
    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingResponse(**result)


async def _enrich_booking(booking: dict) -> dict:
    enriched = dict(booking)

    if booking.get("member_id"):
        try:
            member_result = await directus.get_item("members", booking["member_id"])
            member_data = member_result.get("data", {})
            enriched["member_name"] = member_data.get("name")
        except Exception:
            enriched["member_name"] = None

    if booking.get("coach_id"):
        try:
            coach_result = await directus.get_item("coaches", booking["coach_id"])
            coach_data = coach_result.get("data", {})
            enriched["coach_name"] = coach_data.get("name")
        except Exception:
            enriched["coach_name"] = None

    return enriched
