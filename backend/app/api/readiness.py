from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.services.readiness_service import build_system_readiness

router = APIRouter(prefix="/readiness", tags=["System Readiness"])


@router.get("")
async def get_readiness(db: AsyncSession = Depends(get_db)):
    return await build_system_readiness(db)
