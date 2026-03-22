"""Authentication service for user registration and login."""

from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.user import User
from ..schemas.auth import UserRegisterSchema, UserLoginSchema, TokenSchema


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.utcnow() + expires_delta
    payload = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def register_user(db: AsyncSession, user_data: UserRegisterSchema) -> User:
    """Register a new user."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none() is not None:
        raise ValueError(f"Email {user_data.email} already registered")

    # Create new user
    user = User(
        email=user_data.email,
        display_name=user_data.display_name,
        hashed_password=hash_password(user_data.password),
        sex=user_data.sex,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, login_data: UserLoginSchema) -> tuple[User, str]:
    """Authenticate a user and return user + access token."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(login_data.password, user.hashed_password):
        raise ValueError("Invalid email or password")

    # Create access token
    access_token = create_access_token(user.id)
    return user, access_token
