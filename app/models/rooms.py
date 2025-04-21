from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey

from app.database import Base

class RoomsOrm(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    title: Mapped[str]
    description: Mapped[int | None]
    price: Mapped[int]
    quantity: Mapped[int]
