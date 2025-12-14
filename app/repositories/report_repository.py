from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, between
from app.models.Report import DailyReport
from app.models.Order import Order
from app.models.OrderItem import OrderItem
import logging

logger = logging.getLogger(__name__)

class ReportRepository:
    async def create_daily_report(self, session: AsyncSession, report_data: dict) -> DailyReport:
        """Создание записи отчета"""
        report = DailyReport(**report_data)
        session.add(report)
        await session.commit()
        await session.refresh(report)
        return report

    async def create_bulk_reports(self, session: AsyncSession, reports_data: List[dict]) -> List[DailyReport]:
        """Создание нескольких отчетов"""
        reports = [DailyReport(**data) for data in reports_data]
        session.add_all(reports)
        await session.commit()
        for report in reports:
            await session.refresh(report)
        return reports

    async def get_reports_by_date(
            self,
            session: AsyncSession,
            start_date: date,
            end_date: date
    ) -> List[DailyReport]:
        """Получение отчетов за период"""
        stmt = select(DailyReport).where(
            DailyReport.report_date.between(start_date, end_date)
        ).order_by(DailyReport.report_date.desc(), DailyReport.created_at.desc())

        result = await session.execute(stmt)
        return list(result.scalars().all())
