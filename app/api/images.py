import shutil
from fastapi import APIRouter, UploadFile


router = APIRouter(prefix="/images", tags=["Изображение отелей"])


@router.post("")
def upload_file(file: UploadFile):
    with open(f"app/static/images/{file.filename}", "wb+") as new_file:
        shutil.copyfileobj(file.file, new_file)

    resize_image.delay(image_path)
