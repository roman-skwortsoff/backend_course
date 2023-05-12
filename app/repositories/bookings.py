from app.models.bookings import BookingsOrm
from app.repositories.base import BaseReposirory
from app.repositories.mappers.mappers import BookingDataMapper


class BookingsRepository(BaseReposirory):
    model = BookingsOrm
    mapper = BookingDataMapper