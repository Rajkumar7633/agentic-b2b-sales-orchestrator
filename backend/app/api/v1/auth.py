from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.domain.models.models import AuditLog, User
from app.domain.schemas.schemas import TokenResponse, UserLoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalars().first()

    if not user or not verify_password(body.password, user.hashed_password):
        # Audit failed login attempt
        if user:
            audit = AuditLog(
                tenant_id=user.tenant_id,
                user_id=user.id,
                action="AUTH_LOGIN_FAILED",
                resource_type="User",
                resource_id=user.id,
                details={"email": body.email, "reason": "incorrect_password"},
                ip_address=request.client.host if request.client else None
            )
            db.add(audit)
            await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id
    })

    # Audit successful login
    audit = AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="AUTH_LOGIN_SUCCESS",
        resource_type="User",
        resource_id=user.id,
        details={"email": user.email, "role": user.role},
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    await db.commit()

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        role=user.role,
        tenant_id=user.tenant_id
    )
