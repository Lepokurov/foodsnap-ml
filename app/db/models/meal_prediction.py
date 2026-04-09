from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MealPrediction(Base):
    __tablename__ = "meal_predictions"

    meal_id: Mapped[str] = mapped_column(
        ForeignKey("meal_entries.id", ondelete="CASCADE"),
        primary_key=True,
    )
    raw_label: Mapped[str] = mapped_column(String(120))
    normalized_label: Mapped[str] = mapped_column(String(120), index=True)
    confidence: Mapped[float] = mapped_column()
    model_version: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    meal = relationship("MealEntry", back_populates="prediction")
