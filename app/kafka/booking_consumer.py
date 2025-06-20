import asyncio
import json
import sys
from confluent_kafka import Consumer
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.bookings import BookingService
from app.config import settings
from app.database import async_session_maker
from app.utils.db_manager import DB_Manager
from app.schemas.bookings import BookingAdd

conf = {
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'booking-consumer-group',
    'auto.offset.reset': 'earliest',
}

consumer = Consumer(conf)
consumer.subscribe(['booking-topic'])

print("[🟢] Booking Kafka Consumer started...")


async def handle_booking(user_id: int, booking_data: dict):
    print("!!!!!!!!!!!!!!!!!", booking_data)
    booking_model = BookingAdd(**booking_data)
    async with DB_Manager(session_factory=async_session_maker) as db:
        booking = await BookingService(db).create_booking(user_id, booking_model)
    return booking


async def consume():
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            await asyncio.sleep(0.1)
            continue
        if msg.error():
            print("[❌] Kafka error:", msg.error())
            continue

        try:
            data = json.loads(msg.value().decode("utf-8"))
            user_id = data["user_id"]
            booking_data = data["booking_data"]
            await handle_booking(user_id, booking_data)
            print("[✅] Booking processed for user_id:", user_id)
        except Exception as e:
            print("[❌] Error handling booking:", e)


if __name__ == "__main__":
    asyncio.run(consume())
