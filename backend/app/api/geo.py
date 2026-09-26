from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.services.geo_service import geo_service


router = APIRouter(prefix="/geo", tags=["Geo Intelligence"])


@router.get("/datasets")
async def datasets(db: AsyncSession = Depends(get_db)):
    records = await geo_service.datasets(db)
    return [{
        "id": item.id, "name": item.name, "domain": item.domain,
        "source": item.source, "provider": item.provider, "version": item.version,
        "retrieved_at": item.retrieved_at, "valid_time": item.valid_time,
        "spatial_extent": item.spatial_extent, "temporal_extent": item.temporal_extent,
        "license_reference": item.license_reference, "checksum": item.checksum,
        "provenance": item.provenance, "status": item.status,
        "metadata": item.metadata_info,
    } for item in records]


@router.get("/domains/{domain}")
async def domain_map(domain: str, db: AsyncSession = Depends(get_db)):
    try:
        return await geo_service.domain_map(db, domain)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown environmental domain")
