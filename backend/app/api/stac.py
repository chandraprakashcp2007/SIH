from fastapi import APIRouter
router=APIRouter(prefix="/interop",tags=["Interoperability"])
@router.get("/stac")
async def stac():return {"stac_version":"1.0.0","type":"Catalog","id":"prahari-dataset-metadata","description":"PRAHARI dataset registry metadata; not a claim of live provider connectivity.","links":[{"rel":"self","href":"/api/interop/stac"},{"rel":"data","href":"/api/geo/datasets"}],"operational_status":"METADATA_ONLY","live_provider_claim":False}
