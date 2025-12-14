# app/models/report.py
from sqlalchemy import String, Integer, Date, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from app.models.Base import Base

class DailyReport(Base):
    """Таблица для хранения ежедневных отчетов"""
    __tablename__ = "daily_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    product_count: Mapped[int] = mapped_column(Integer, default=0, comment="Количество продукции в заказе")
    total_items: Mapped[int] = mapped_column(Integer, default=0, comment="Общее количество единиц товара")
    total_amount: Mapped[float] = mapped_column(Float, default=0.0, comment="Общая сумма заказа")
    order_status: Mapped[str] = mapped_column(String(20), default="pending", comment="Статус заказа")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DailyReport {self.report_date} Order:{self.order_id}>"