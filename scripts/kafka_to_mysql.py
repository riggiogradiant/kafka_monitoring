import json
import os
from kafka import KafkaConsumer
import mysql.connector


# Configuración de Kafka desde variables de entorno
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:29092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'dbserver1.public.test_sync')
KAFKA_GROUP_ID = os.environ.get('KAFKA_GROUP_ID', 'sync-mysql')

# Configuración de MySQL desde variables de entorno
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
    'user': os.environ.get('MYSQL_USER', 'debezium'),
    'password': os.environ.get('MYSQL_PASSWORD', 'dbz'),
    'database': os.environ.get('MYSQL_DATABASE', 'inventory')
}

def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    print('Esperando mensajes de Kafka...')
    for msg in consumer:
        payload = msg.value.get('payload')
        if not payload:
            continue
        after = payload.get('after')
        op = payload.get('op')
        if after and op == 'c':  # Solo inserts
            id_ = after['id']
            data = after['data']
            try:
                cursor.execute(
                    "INSERT INTO test_sync (id, data) VALUES (%s, %s) ON DUPLICATE KEY UPDATE data=VALUES(data)",
                    (id_, data)
                )
                conn.commit()
                print(f"Insertado en MySQL: id={id_}, data={data}")
            except Exception as e:
                print(f"Error insertando en MySQL: {e}")

if __name__ == '__main__':
    main()
