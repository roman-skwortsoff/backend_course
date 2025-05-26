from app.database import async_session_maker_null
from app.schemas.hotels import HotelAdd
from app.utils.db_manager import DB_Manager


# async def test_add_hotel():
#     hotel_data = HotelAdd(title="Hotel 5", location="Сочи")
#     async with DB_Manager(session_factory=async_session_maker_null) as db: # можно async with DB_Manager(session_factory=async_session_maker) as db:
#         new_hotel_data = await db.hotels.add(hotel_data)
#         print("!!!!!!!!!!!!", f"{new_hotel_data=}")
#         await db.commit()


async def test_add_hotel(db):
    hotel_data = HotelAdd(title="Hotel 5", location="Сочи")
    new_hotel_data = await db.hotels.add(hotel_data)
    print("!!!!!!!!!!!!", f"{new_hotel_data=}")
    await db.commit()