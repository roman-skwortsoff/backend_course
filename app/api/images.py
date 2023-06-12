from fastapi import APIRouter, UploadFile

from app.services.images import ImagesService


router = APIRouter(prefix="/images", tags=["Изображение отелей"])


@router.post("")
def upload_file(file: UploadFile):
    ImagesService().upload_file(file)
