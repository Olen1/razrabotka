# app/broker.py
import sqlite3
import json
import asyncio
from typing import Any
import logging

logger = logging.getLogger(__name__)

class SQLiteBroker:
    """Простой брокер на основе SQLite для локальной разработки"""

    def __init__(self, db_path: str = "queue.db"):
        self.db_path = db_path
        self._is_connected = False
        self._callbacks = {}
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных для очередей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                queue TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queue_processed ON messages(queue, processed)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON messages(created_at)')

        conn.commit()
        conn.close()

    async def start(self):
        """Запуск брокера"""
        self._is_connected = True
        logger.info("SQLiteBroker started")

    async def close(self):
        """Остановка брокера"""
        self._is_connected = False
        logger.info("SQLiteBroker closed")

    def subscriber(self, queue: str):
        """Декоратор для подписки на очередь"""
        def decorator(func):
            if queue not in self._callbacks:
                self._callbacks[queue] = []
            self._callbacks[queue].append(func)
            return func
        return decorator

    async def publish(self, message: Any, queue: str) -> None:
        """Публикация сообщения в очередь"""
        if not self._is_connected:
            raise RuntimeError("Broker is not connected")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Сериализуем сообщение
        if hasattr(message, 'dict'):
            message_data = message.dict()
        else:
            message_data = message

        message_json = json.dumps(message_data, default=str)

        # Сохраняем сообщение в базу
        cursor.execute(
            "INSERT INTO messages (queue, message) VALUES (?, ?)",
            (queue, message_json)
        )

        conn.commit()
        conn.close()

        logger.info("Message published to queue '%s': %s", queue, message_data)

        # Запускаем обработку сообщений
        asyncio.create_task(self._process_messages())

    async def _process_messages(self):
        """Обработка сообщений из очереди"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Получаем непрочитанные сообщения
            cursor.execute(
                "SELECT id, queue, message FROM messages WHERE processed = FALSE ORDER BY created_at ASC"
            )
            messages = cursor.fetchall()

            for msg_id, queue, message_json in messages:
                if queue in self._callbacks:
                    try:
                        message_data = json.loads(message_json)

                        # Вызываем все подписчики этой очереди
                        for callback in self._callbacks[queue]:
                            try:
                                await callback(message_data)
                                # Помечаем сообщение как обработанное
                                cursor.execute(
                                    "UPDATE messages SET processed = TRUE WHERE id = ?",
                                    (msg_id,)
                                )
                                conn.commit()
                                logger.info("Message %s processed successfully", msg_id)
                            except Exception as e:  # pylint: disable=broad-except
                                logger.error("Error processing message %s: %s", msg_id, e)
                                # Можно добавить логику повторных попыток

                    except json.JSONDecodeError as e:
                        logger.error("Invalid JSON in message %s: %s", msg_id, e)
                        cursor.execute(
                            "UPDATE messages SET processed = TRUE WHERE id = ?",
                            (msg_id,)
                        )
                        conn.commit()

            conn.close()
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error in message processing: %s", e)

# Создаем экземпляр брокера
broker = SQLiteBroker()