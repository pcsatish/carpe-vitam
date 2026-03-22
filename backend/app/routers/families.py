"""Families router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..dependencies import get_current_user
from ..models.family import Family, FamilyMember, FamilyMemberRole
from ..models.user import User
from ..schemas.families import (
    FamilyCreateSchema,
    FamilySchema,
    FamilyMemberCreateSchema,
    FamilyMemberSchema,
)

router = APIRouter()


@router.post("", response_model=FamilySchema, status_code=status.HTTP_201_CREATED)
async def create_family(
    payload: FamilyCreateSchema,
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Create a new family. Current user is added as ADMIN."""
    family = Family(name=payload.name, created_by=current_user.id)
    db.add(family)
    await db.flush()  # get family.id before adding member

    admin_member = FamilyMember(
        family_id=family.id,
        user_id=current_user.id,
        display_name=current_user.display_name,
        role=FamilyMemberRole.ADMIN,
    )
    db.add(admin_member)
    await db.commit()
    await db.refresh(family)
    return family


@router.get("", response_model=list[FamilySchema])
async def list_families(
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """List families the current user belongs to."""
    result = await db.execute(
        select(Family)
        .join(FamilyMember, FamilyMember.family_id == Family.id)
        .where(FamilyMember.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/{family_id}/members", response_model=list[FamilyMemberSchema])
async def list_members(
    family_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """List members of a family. Requires membership."""
    membership = await _require_membership(db, family_id, current_user.id)  # noqa: F841

    result = await db.execute(
        select(FamilyMember).where(FamilyMember.family_id == family_id)
    )
    return result.scalars().all()


@router.post(
    "/{family_id}/members",
    response_model=FamilyMemberSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    family_id: str,
    payload: FamilyMemberCreateSchema,
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Add a member to a family. Requires ADMIN role."""
    await _require_admin(db, family_id, current_user.id)

    # Resolve email to user_id if provided
    user_id = payload.user_id
    if payload.email and not user_id:
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No registered user with email {payload.email}",
            )
        user_id = user.id

    member = FamilyMember(
        family_id=family_id,
        user_id=user_id,
        display_name=payload.display_name,
        date_of_birth=payload.date_of_birth,
        sex=payload.sex,
        role=payload.role,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def _require_membership(
    db: AsyncSession, family_id: str, user_id: str
) -> FamilyMember:
    result = await db.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    return member


async def _require_admin(db: AsyncSession, family_id: str, user_id: str) -> FamilyMember:
    member = await _require_membership(db, family_id, user_id)
    if member.role != FamilyMemberRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return member
