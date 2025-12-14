# client.py
import asyncio
import logging
from datetime import date
from tasks import broker, report_generator

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_manual_tasks():
    """Отправка задач вручную"""
    try:
        await broker.startup()

        logger.info("TaskIQ client started")

        # 1. Генерация отчета за конкретную дату
        specific_date = date(2024, 1, 15)
        logger.info(f"Sending manual daily report task for {specific_date}...")

        # Создаем задачу для генерации отчета
        result = await report_generator.generate_daily_order_report(specific_date)
        logger.info(f"Manual report generated: {len(result.get('orders', []))} orders")

        # 2. Генерация отчета по топ продуктам
        logger.info("Sending manual top products report task...")
        top_products = await report_generator.generate_top_products_report(30, 5)
        logger.info(f"Top products report: {len(top_products.get('top_products', []))} products")

        # 3. Отправка отложенной задачи через брокер
        logger.info("Sending delayed task via broker...")
        task = await broker.kick(
            "generate_top_products_task",
            args=[7, 5],  # За последние 7 дней, топ 5
            delay=10  # Задержка 10 секунд
        )
        logger.info(f"Delayed task sent with ID: {task.task_id}")

        # Ждем выполнения задачи
        await asyncio.sleep(15)

    except Exception as e:
        logger.error(f"Client error: {e}")
    finally:
        await broker.shutdown()
        logger.info("Client stopped")

async def test_all_tasks():
    """Тестирование всех задач"""
    try:
        await broker.startup()

        logger.info("Testing all scheduled tasks...")

        # Получаем список всех доступных задач
        tasks = list(broker.available_tasks.keys())
        logger.info(f"Available tasks: {tasks}")

        # Тестируем каждую задачу
        test_results = {}

        for task_name in tasks:
            try:
                logger.info(f"Testing task: {task_name}")

                if task_name == "generate_daily_report_task":
                    result = await broker.kick(task_name)
                elif task_name == "generate_top_products_task":
                    result = await broker.kick(task_name, args=[7, 3])
                elif task_name == "check_low_stock_task":
                    result = await broker.kick(task_name)
                elif task_name == "system_monitor_task":
                    result = await broker.kick(task_name, args=["Test Run"])
                else:
                    result = await broker.kick(task_name)

                test_results[task_name] = "SUCCESS"
                logger.info(f"  {task_name}: ✓ SUCCESS")

            except Exception as e:
                test_results[task_name] = f"FAILED: {e}"
                logger.error(f"  {task_name}: ✗ FAILED - {e}")

        # Вывод результатов
        logger.info("\n" + "="*50)
        logger.info("TEST RESULTS:")
        for task, status in test_results.items():
            logger.info(f"  {task}: {status}")

    except Exception as e:
        logger.error(f"Test error: {e}")
    finally:
        await broker.shutdown()

if __name__ == "__main__":
    # Запускаем тестирование
    asyncio.run(test_all_tasks())