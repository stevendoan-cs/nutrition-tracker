from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    calories: Mapped[float] = mapped_column(nullable=False)
    protein: Mapped[float] = mapped_column(default=0.0)
    carbs: Mapped[float] = mapped_column(default=0.0)
    fat: Mapped[float] = mapped_column(default=0.0)