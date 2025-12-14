# app/services/report_service.py (дополнение)
from typing import List, Dict, Any
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.Report import DailyReport
from app.repositories.order_repository import OrderRepository
from app.repositories.product_reposutory import ProductRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.report_schema import (
    ReportStatistics,
    ReportResponse
)
import logging

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(
            self,
            report_repository: ReportRepository,
            order_repository: OrderRepository,
            product_repository: ProductRepository
    ):
        self.report_repository = report_repository
        self.order_repository = order_repository
        self.product_repository = product_repository

    async def get_report_by_date(
            self,
            session: AsyncSession,
            report_date: date,
            include_details: bool = True
    ) -> ReportResponse:
        """
        Получение отчета за конкретную дату
        """
        try:
            # Получаем все отчеты за указанную дату
            reports = await self.report_repository.get_reports_by_filter(
                session,
                count=1000,
                page=1,
                report_date=report_date
            )

            if not reports:
                return ReportResponse(
                    success=False,
                    report_date=report_date,
                    generated_at=datetime.now(),
                    message=f"No reports found for date {report_date}"
                )

            # Рассчитываем статистику
            statistics = await self._calculate_statistics(session, reports, report_date)

            # Подготавливаем ответ
            response = ReportResponse(
                success=True,
                report_date=report_date,
                generated_at=datetime.now(),
                statistics=statistics,
                message=f"Report for {report_date} retrieved successfully"
            )

            # Если нужно включить детали
            if include_details:
                response.reports = [
                    DailyReportResponse(
                        id=report.id,
                        report_date=report.report_date,
                        order_id=report.order_id,
                        user_id=report.user_id,
                        product_count=report.product_count,
                        total_items=report.total_items,
                        total_amount=report.total_amount,
                        order_status=report.order_status,
                        created_at=report.created_at
                    )
                    for report in reports
                ]

            logger.info(f"Report retrieved for {report_date}: {len(reports)} orders")
            return response

        except Exception as e:
            logger.error(f"Error getting report for {report_date}: {e}")
            raise

    async def _calculate_statistics(
            self,
            session: AsyncSession,
            reports: List[DailyReport],
            report_date: date
    ) -> ReportStatistics:
        """Расчет статистики по отчетам"""
        if not reports:
            return ReportStatistics(
                report_date=report_date,
                total_orders=0,
                unique_users=0,
                total_products=0,
                total_items=0,
                total_revenue=0.0,
                avg_order_value=0.0,
                avg_products_per_order=0.0
            )

        # Собираем статистику
        unique_users = len(set(report.user_id for report in reports))
        total_orders = len(reports)
        total_products = sum(report.product_count for report in reports)
        total_items = sum(report.total_items for report in reports)
        total_revenue = sum(report.total_amount for report in reports)

        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        avg_products_per_order = total_products / total_orders if total_orders > 0 else 0

        return ReportStatistics(
            report_date=report_date,
            total_orders=total_orders,
            unique_users=unique_users,
            total_products=total_products,
            total_items=total_items,
            total_revenue=round(total_revenue, 2),
            avg_order_value=round(avg_order_value, 2),
            avg_products_per_order=round(avg_products_per_order, 2)
        )

