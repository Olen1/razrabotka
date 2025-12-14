"""
Запуск планировщика Taskiq:
taskiq scheduler tasks:broker
"""
import asyncio
import logging
from tasks import broker, scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_scheduler():
    """Запуск планировщика"""
    try:
        logger.info("Starting TaskIQ scheduler...")

        # Запускаем брокер
        await broker.startup()

        # Запускаем планировщик
        scheduler.start()


        for task_name in broker.available_tasks.keys():
            logger.info(f"  - {task_name}")

        # Бесконечный цикл
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down scheduler...")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
    finally:
        await broker.shutdown()
        scheduler.shutdown()
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    asyncio.run(run_scheduler())