# Escenario base de monitorización con Kafka, Debezium y 2 bases de datos

Este entorno permite simular un flujo de captura de cambios (CDC) usando Debezium, Kafka y dos bases de datos (PostgreSQL y MySQL), ideal para pruebas de monitorización.

## Servicios incluidos
- **Zookeeper**: Coordinador de Kafka.
- **Kafka**: Broker de mensajería.
- **PostgreSQL**: Base de datos origen 1.
- **MySQL**: Base de datos origen 2.
- **Debezium**: Plataforma de CDC para capturar cambios en las bases de datos y enviarlos a Kafka.

## Requisitos previos
- Docker y Docker Compose instalados.


## Uso rápido


### 1. Levantar el entorno completo
Lanza todos los servicios (Kafka, Zookeeper, PostgreSQL, MySQL y Debezium) con:
```bash
docker compose up -d --build
```

### 2. Crear la tabla de ejemplo (si no existe)
Ejecuta el script para crear la tabla en ambas bases de datos desde tu máquina:
```bash
python scripts/init_tables.py
```
O bien, puedes crearla manualmente en PostgreSQL:
```bash
docker exec -it kafka_monitoring-postgres-1 psql -U debezium -d inventory
```
Y dentro de psql:
```sql
CREATE TABLE IF NOT EXISTS test_sync (
    id SERIAL PRIMARY KEY,
    data TEXT
);
```
Sal con `\q`.

### 3. Registrar el conector Debezium para PostgreSQL
Ejecuta este comando desde tu máquina (no desde un contenedor):
```bash
curl -X POST http://localhost:8083/connectors -H 'Content-Type: application/json' -d '{
  "name": "inventory-connector-postgres",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "dbz",
    "database.dbname": "inventory",
    "database.server.name": "dbserver1",
    "plugin.name": "pgoutput",
    "table.include.list": "public.test_sync",
    "topic.prefix": "dbserver1"
  }
}'
```

### 4. Lanzar el consumidor Python para sincronizar datos
Ejecuta el consumidor desde tu máquina. Para leer todos los mensajes desde el principio del topic, usa un nuevo `KAFKA_GROUP_ID`:
```bash
KAFKA_BROKER=localhost:29092 KAFKA_TOPIC=dbserver1.public.test_sync KAFKA_GROUP_ID=sync-mysql-test python scripts/kafka_to_mysql.py
```
Deja esta terminal abierta, el script mostrará los mensajes insertados en MySQL.

### 5. Probar la sincronización end-to-end
1. Inserta un dato en PostgreSQL (puedes hacerlo desde psql o usando DBeaver, etc.):
   ```sql
   INSERT INTO test_sync (data) VALUES ('mensaje de prueba desde postgres');
   ```
2. Observa en la terminal del consumidor Python que se detecta el mensaje y se inserta en MySQL.
3. Comprueba en MySQL:
   ```bash
   docker exec -it kafka_monitoring-mysql-1 mysql -u debezium -pdbz inventory
   SELECT * FROM test_sync;
   ```

### 6. Parar y limpiar el entorno
```bash
docker compose down -v
```


## Monitorización de Kafka con Prometheus y Grafana

### Servicios añadidos
- **kafka-jmx-exporter**: expone métricas JMX de Kafka en formato Prometheus.
- **prometheus**: recolecta métricas de kafka-jmx-exporter.
- **grafana**: visualiza dashboards de Kafka.

### Secuencia para monitorizar
1. Levanta el entorno completo:
  ```bash
  docker compose up -d --build
  ```
2. Accede a Prometheus en http://localhost:9090 y verifica el target kafka-jmx-exporter.
3. Accede a Grafana en http://localhost:3000 (usuario admin, contraseña admin).
4. Añade Prometheus como datasource en Grafana (URL: http://prometheus:9090).
5. Importa dashboards oficiales de Kafka (por ejemplo, ID 7589: "Kafka Overview").
6. Visualiza métricas clave: throughput, lag, estado de brokers, topics, etc.

### Configuración
- El archivo `monitoring/prometheus.yml` define el target kafka-jmx-exporter.
- El archivo `monitoring/jmx-exporter-config.yml` define las métricas JMX a exportar.

### Extensiones
- Puedes añadir exporters para consumidores (Kafka Exporter, Burrow).
- Puedes definir alertas en Grafana para lag, brokers offline, etc.

---
Este entorno permite monitorizar Kafka de forma flexible y extensible usando herramientas open source.

---

Este entorno es la base para experimentar con monitorización de Kafka y CDC.
# kafka_monitoring