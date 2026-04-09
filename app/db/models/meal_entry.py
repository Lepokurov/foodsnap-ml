from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MealEntry(Base):
    __tablename__ = "meal_entries"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), index=True)
    image_url: Mapped[str] = mapped_column(String(1024))
    image_storage: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    meal_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    recognized_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    estimated_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="meals")
    prediction = relationship(
        "MealPrediction",
        back_populates="meal",
        uselist=False,
        cascade="all, delete-orphan",
    )
