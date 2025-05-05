from sqlalchemy import select, insert

from app.models.bookings import BookingsOrm
from app.repositories.base import BaseReposirory
from app.schemas.bookings import Booking


class BookingsRepository(BaseReposirory):
    model = BookingsOrm
    schema = Booking