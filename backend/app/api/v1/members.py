from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.directus import get_directus_client
from app.models import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
)

router = APIRouter(prefix="/members", tags=["members"])
directus = get_directus_client()


@router.post("/", response_model=MemberResponse)
async def create_member(member: MemberCreate):
    result = await directus.create_item("members", member.model_dump())
    data = result.get("data", {})
    return MemberResponse(**data)


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(member_id: str):
    result = await directus.get_item("members", member_id)
    data = result.get("data")
    if not data:
        raise HTTPException(status_code=404, detail="Member not found")
    return MemberResponse(**data)


@router.get("/", response_model=list[MemberResponse])
async def list_members(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    skill_level: Optional[str] = None
):
    filter_cond = {}
    if skill_level:
        filter_cond["skill_level"] = {"_eq": skill_level}

    result = await directus.query(
        "members",
        filter=filter_cond if filter_cond else None,
        limit=limit,
        offset=offset
    )
    members = result.get("data", [])
    return [MemberResponse(**m) for m in members]


@router.patch("/{member_id}", response_model=MemberResponse)
async def update_member(member_id: str, member: MemberUpdate):
    update_data = {k: v for k, v in member.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await directus.update_item("members", member_id, update_data)
    data = result.get("data")
    if not data:
        raise HTTPException(status_code=404, detail="Member not found")
    return MemberResponse(**data)


@router.delete("/{member_id}")
async def delete_member(member_id: str):
    await directus.delete_item("members", member_id)
    return {"message": "Member deleted successfully"}
