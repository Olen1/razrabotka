
import asyncio
import logging
from taskiq_aio_pika import AioPikaBroker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("=== Запуск TaskIQ Worker ===")

    # Конфигурация брокера
    broker = AioPikaBroker(
        url="amqp://guest:guest@localhost:5672/",
        declare_exchange=True,
        declare_queues=True,
        qos=1,
        max_priority=10,
        reconnect_interval=5,
        connect_timeout=10,
    )

    try:
        await broker.startup()
        logger.info("Брокер успешно запущен и готов к работе!")
        logger.info("Ожидание задач... (Нажмите Ctrl+C для остановки)")

        await asyncio.Event().wait()

    except KeyboardInterrupt:
        logger.info("\nПолучен сигнал прерывания. Останавливаюсь...")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        await broker.shutdown()
        logger.info("Воркер остановлен.")

if __name__ == "__main__":
    asyncio.run(main())