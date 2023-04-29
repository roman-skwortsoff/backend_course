from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import CITEXT

from app.database import Base

class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(CITEXT(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))