import typing

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from app.database import Base

if typing.TYPE_CHECKING:
    from app.models import RoomsOrm


class FacilitiesOrm(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))

    rooms: Mapped[list["RoomsOrm"]] = relationship(
        back_populates="facilities",
        secondary="rooms_facilities",
    )


class RoomsFacilitiesOrm(Base):
    __tablename__ = "rooms_facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id = mapped_column(ForeignKey("rooms.id"))
    facility_id = mapped_column(ForeignKey("facilities.id"))
