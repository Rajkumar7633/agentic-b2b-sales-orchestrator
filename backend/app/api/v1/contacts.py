
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import UserContext, get_current_user
from app.domain.models.models import Contact
from app.domain.schemas.schemas import ContactSchema

router = APIRouter(prefix="/contacts", tags=["Named Contacts"])


@router.get("", response_model=list[ContactSchema])
async def list_contacts(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    result = await db.execute(select(Contact).where(Contact.tenant_id == user.tenant_id))
    return result.scalars().all()


@router.get("/{contact_id}", response_model=ContactSchema)
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.tenant_id == user.tenant_id)
    )
    contact = result.scalars().first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact
