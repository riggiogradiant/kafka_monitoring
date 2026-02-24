import requests
import json

# Configuración del conector Debezium para PostgreSQL
connector_config = {
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
        "table.include.list": "public.test_sync"
    }
}

resp = requests.post(
    "http://localhost:8083/connectors",
    headers={"Content-Type": "application/json"},
    data=json.dumps(connector_config)
)

print("Status:", resp.status_code)
print("Response:", resp.text)
