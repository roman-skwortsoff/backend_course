import json

from fastapi import APIRouter, Body
from app.api.dependencies import DBDep
from app.schemas.facilities import FacilityAdd
from app.setup import redis_manager
from app.tasks.tasks import test_task

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", summary="Весь список удобств")
async def get_all_facilities(db: DBDep):
    test_task.delay()
    facilities_from_cache = await redis_manager.get("facilities")
    print(facilities_from_cache)
    if not facilities_from_cache:
        facilities = await db.facilities.get_all()
        facilities_schemas = [f.model_dump() for f in facilities]
        facilities_json = json.dumps(facilities_schemas)
        await redis_manager.set("facilities", facilities_json, 10)
        return facilities
    else:
        print("Иду в кэш")
        facilities_dict = json.loads(facilities_from_cache)
        return facilities_dict


@router.post("")
async def create_facility(
    db: DBDep, facility_data: FacilityAdd = Body(openapi_examples={})
):
    facility = await db.facilities.add(facility_data)
    await db.commit()
    return {"status": "OK", "room": facility}
