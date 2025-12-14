
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from litestar import Controller, get, post
from litestar.params import Parameter, Body
from litestar.exceptions import HTTPException
from litestar.response import Response
from litestar.status_codes import HTTP_404_NOT_FOUND
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.report_schema import (
    ReportRequest,
    ReportResponse,
    ReportStatistics
)
import logging

logger = logging.getLogger(__name__)

class ReportController(Controller):
    path = "/api/reports"


    @post("/")
    async def get_report(
            self,
            session: AsyncSession,
            data: ReportRequest = Body(
                title="Report Request",
                description="Получить отчет за конкретную дату"
            )
    ) -> ReportResponse:
        """
        Получить отчет за конкретную дату

        - **report_date**: Дата отчета в формате YYYY-MM-DD
        - **include_details**: Включать ли детали по каждому заказу (по умолчанию True)
        """
        try:
            report = await self.report_service.generate_and_get_report(
                session,
                data.report_date,
                data.include_details
            )

            if not report.success:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail=report.message
                )

            return report

        except Exception as e:
            logger.error(f"Error getting report for {data.report_date}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get report: {str(e)}"
            )

    @get("/{report_date:str}")
    async def get_report_by_date(
            self,
            session: AsyncSession,
            report_date: date = Parameter(
                title="Report Date",
                description="Дата отчета в формате YYYY-MM-DD"
            ),
            details: bool = Parameter(
                default=True,
                description="Включать детали по заказам"
            )
    ) -> ReportResponse:
        """
        Получить отчет за дату (GET версия)

        Пример: /api/reports/2024-01-15?details=true
        """
        try:
            return await self.report_service.generate_and_get_report(
                session, report_date, details
            )
        except Exception as e:
            logger.error(f"Error in GET report for {report_date}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get report: {str(e)}"
            )

