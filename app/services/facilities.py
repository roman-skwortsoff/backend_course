import json

from app.schemas.facilities import FacilityAdd
from app.services.base import BaseService
from app.tasks.tasks import test_task
from app.setup import redis_manager


class FacilityService(BaseService):
    async def get_all_facilities(self):
        test_task.delay()
        facilities_from_cache = await redis_manager.get("facilities")
        print(facilities_from_cache)
        if not facilities_from_cache:
            facilities = await self.db.facilities.get_all()
            facilities_schemas = [f.model_dump() for f in facilities]
            facilities_json = json.dumps(facilities_schemas)
            await redis_manager.set("facilities", facilities_json, 10)
            return facilities
        else:
            print("Иду в кэш")
            facilities_dict = json.loads(facilities_from_cache)
            return facilities_dict

    async def create_facility(self, facility_data: FacilityAdd):
        facility = await self.db.facilities.add(facility_data)
        await self.db.commit()
        return facility
