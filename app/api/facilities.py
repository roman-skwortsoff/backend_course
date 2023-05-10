from datetime import date

from fastapi import Query, APIRouter, Body
from app.api.dependencies import PaginationDep, DBDep
from app.repositories.facilities import FacilitiesRepository
from app.schemas.facilities import FacilityAdd, Facilities

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", summary="Весь список удобств")
async def get_all_facilities(
        db: DBDep,
        ):
    return await db.facilities.get_all(
    )

@router.post("")
async def create_facility(db: DBDep,
                          facility_data: FacilityAdd = Body(openapi_examples={})):
    facility = await db.facilities.add(facility_data)
    await db.commit()
    return {"status": "OK", "room": facility}