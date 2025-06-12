from fastapi import APIRouter, Body

from app.api.dependencies import DBDep
from app.schemas.facilities import FacilityAdd
from app.services.facilities import FacilityService

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", summary="Весь список удобств")
async def get_all_facilities(db: DBDep):
    return await FacilityService(db).get_all_facilities()


@router.post("")
async def create_facility(
    db: DBDep, facility_data: FacilityAdd = Body(openapi_examples={})
):
    facility = await FacilityService(db).create_facility(facility_data)
    return {"status": "OK", "room": facility}
