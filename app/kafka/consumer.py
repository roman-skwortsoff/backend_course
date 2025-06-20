import sys
from confluent_kafka import Consumer
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config import settings

conf = {
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'fastapi-consumer-group',
    'auto.offset.reset': 'earliest',
}

consumer = Consumer(conf)
consumer.subscribe(['test-topic'])

print("[🟢] Kafka Consumer started...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error:", msg.error())
            continue
        print(f"[📥] Received message: {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
