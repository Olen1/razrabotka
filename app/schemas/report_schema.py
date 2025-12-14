# app/schemas/report_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime

class DailyReportBase(BaseModel):
    report_date: date = Field(..., description="Дата отчета")
    order_id: str = Field(..., description="ID заказа")
    user_id: str = Field(..., description="ID пользователя")
    product_count: int = Field(..., description="Количество продукции в заказе")
    total_items: int = Field(..., description="Общее количество единиц товара")
    total_amount: float = Field(..., description="Общая сумма заказа")
    order_status: str = Field(..., description="Статус заказа")

class DailyReportCreate(DailyReportBase):
    pass

class DailyReportResponse(DailyReportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReportStatistics(BaseModel):
    """Статистика по отчету"""
    report_date: date
    total_orders: int = Field(..., description="Всего заказов")
    unique_users: int = Field(..., description="Уникальных пользователей")
    total_products: int = Field(..., description="Всего продукции в заказах")
    total_items: int = Field(..., description="Всего единиц товара")
    total_revenue: float = Field(..., description="Общая выручка")
    avg_order_value: float = Field(..., description="Средний чек")
    avg_products_per_order: float = Field(..., description="Среднее количество продукции в заказе")

class DailyReportSummary(BaseModel):
    """Сводка по дню"""
    report_date: date
    reports: List[DailyReportResponse]
    statistics: ReportStatistics

class ReportRequest(BaseModel):
    """Запрос на получение отчета"""
    report_date: date = Field(..., description="Дата отчета (YYYY-MM-DD)")
    include_details: bool = Field(True, description="Включать детали по каждому заказу")

class ReportResponse(BaseModel):
    """Ответ с отчетом"""
    success: bool = Field(..., description="Успешность выполнения")
    report_date: date = Field(..., description="Дата отчета")
    generated_at: datetime = Field(..., description="Время генерации отчета")
    statistics: Optional[ReportStatistics] = Field(None, description="Статистика")
    reports: Optional[List[DailyReportResponse]] = Field(None, description="Детальные отчеты")
    message: Optional[str] = Field(None, description="Сообщение")