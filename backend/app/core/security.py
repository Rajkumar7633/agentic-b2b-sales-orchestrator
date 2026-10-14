from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    # bcrypt has a 72-byte limit; truncate to avoid ValueError
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


class UserContext:
    def __init__(self, user_id: str, email: str, role: str, tenant_id: str):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.tenant_id = tenant_id


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> UserContext:
    # Default fallback user for dev/testing when token isn't provided
    if not token:
        return UserContext(
            user_id="usr_admin_001",
            email="admin@nexora.ai",
            role="ADMIN",
            tenant_id=settings.DEFAULT_TENANT_ID
        )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub", "usr_admin_001")
        email: str = payload.get("email", "admin@nexora.ai")
        role: str = payload.get("role", "ADMIN")
        tenant_id: str = payload.get("tenant_id", settings.DEFAULT_TENANT_ID)
        return UserContext(user_id=user_id, email=email, role=role, tenant_id=tenant_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
