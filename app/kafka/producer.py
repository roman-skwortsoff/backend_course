from confluent_kafka import Producer
from app.config import settings


conf = {'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS}
producer = Producer(**conf)


def delivery_report(err, msg):
    if err is not None:
        print(f"[❌] Delivery failed: {err}")
    else:
        print(f"[✅] Message delivered to {msg.topic()} [{msg.partition()}]")


def send_message(topic: str, message: str):
    producer.produce(topic, message.encode('utf-8'), callback=delivery_report)
    producer.flush()
