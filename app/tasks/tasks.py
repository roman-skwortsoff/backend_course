import asyncio
import logging
import os
from PIL import Image
from time import sleep

from app.database import async_session_maker_null
from app.tasks.celery_app import celery_instance
from app.utils.db_manager import DB_Manager


@celery_instance.task
def test_task():
    sleep(5)
    print("Я молодец")


@celery_instance.task
def resize_image(image_path: str):
    sizes = [1000, 500, 200]
    output_folder = "src/static/images"

    # Открываем изображение
    img = Image.open(image_path)

    # Получаем имя файла и его расширение
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    # Проходим по каждому размеру
    for size in sizes:
        # Сжимаем изображение
        img_resized = img.resize(
            (size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS
        )

        # Формируем имя нового файла
        new_file_name = f"{name}_{size}px{ext}"

        # Полный путь для сохранения
        output_path = os.path.join(output_folder, new_file_name)

        # Сохраняем изображение
        img_resized.save(output_path)

    print(
        f"Изображение сохранено в следующих размерах: {sizes} в папке {output_folder}"
    )


async def get_bookings_with_today_checkin():
    print("Я запускаюсь")
    async with DB_Manager(session_factory=async_session_maker_null) as db:
        booking = await db.bookings.get_booking_with_today_checkin()
        logging.debug(f"{booking=}")


@celery_instance.task(name="booking_today_checkin")
def test_booking_today_checkin():
    asyncio.run(get_bookings_with_today_checkin())
