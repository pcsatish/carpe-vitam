from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..dependencies import get_current_user
from ..schemas.auth import UserRegisterSchema, UserLoginSchema, TokenSchema, UserSchema
from ..services.auth_service import register_user, login_user

router = APIRouter()


@router.post("/register", response_model=TokenSchema)
async def register(
    user_data: UserRegisterSchema,
    db: AsyncSession = Depends(get_db_session),
):
    """Register a new user."""
    try:
        user = await register_user(db, user_data)
        from ..services.auth_service import create_access_token
        access_token = create_access_token(user.id)
        return TokenSchema(access_token=access_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenSchema)
async def login(
    login_data: UserLoginSchema,
    db: AsyncSession = Depends(get_db_session),
):
    """Login user and return JWT token."""
    try:
        user, access_token = await login_user(db, login_data)
        return TokenSchema(access_token=access_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/refresh", response_model=TokenSchema)
async def refresh(
    current_user = Depends(get_current_user),
):
    """Refresh JWT token."""
    from ..services.auth_service import create_access_token
    access_token = create_access_token(current_user.id)
    return TokenSchema(access_token=access_token)


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user = Depends(get_current_user),
):
    """Get current user info."""
    return current_user
