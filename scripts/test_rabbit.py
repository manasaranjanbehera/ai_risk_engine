# scripts/test_rabbit.py
import sys
from pathlib import Path

# Ensure project root is on the path when running this script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from app.infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher

async def test():
    publisher = RabbitMQPublisher()

    await publisher.publish(
        exchange_name="risk_exchange",
        routing_key="risk.created",
        message={"event": "risk_triggered"},
        idempotency_key="key123",
    )

    print("Published")

asyncio.run(test())
