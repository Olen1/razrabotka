
from taskiq_aio_pika import AioPikaBroker
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from datetime import date, timedelta, datetime
import logging



# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем брокер
broker = AioPikaBroker(
    "amqp://guest:guest@localhost:5672/",
    exchange_name="taskiq_exchange",
    queue_name="taskiq_queue"
)

# Создаем планировщик
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

# Задача: Генерация ежедневного отчета
@broker.task(
    schedule=[
        {
            "cron": "0 23 * * *",  # Каждый день в 23:00
            "args": [],
            "kwargs": {},
            "schedule_id": "generate_daily_report",
            "labels": {
                "name": "Daily Report Generator",
                "description": "Generates daily order reports at 23:00"
            }
        }
    ]
)
async def generate_daily_report():
    """Задача для генерации ежедневного отчета"""
    try:
        from app.services.report_service import ReportService
        from app.repositories.report_repository import ReportRepository
        from app.repositories.order_repository import OrderRepository
        from app.repositories.product_reposutory import ProductRepository
        from app.database import async_session_maker

        report_date = date.today() - timedelta(days=1)  # Вчерашний день

        async with async_session_maker() as session:
            report_service = ReportService(
                ReportRepository(),
                OrderRepository(),
                ProductRepository()
            )

            reports = await report_service.generate_daily_report(session, report_date)
            logger.info(f"Generated daily report for {report_date}: {len(reports)} orders")

            return {
                "status": "success",
                "report_date": report_date.isoformat(),
                "orders_processed": len(reports),
                "generated_at": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        return {
            "status": "error",
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }

