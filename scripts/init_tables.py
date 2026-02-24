import psycopg2
import mysql.connector

# Configuración de PostgreSQL
pg_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="debezium",
    password="dbz",
    dbname="inventory"
)
pg_cur = pg_conn.cursor()

# Configuración de MySQL
my_conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="debezium",
    password="dbz",
    database="inventory"
)
my_cur = my_conn.cursor()

# Crear tabla de ejemplo en ambas bases de datos
pg_cur.execute("""
CREATE TABLE IF NOT EXISTS test_sync (
    id SERIAL PRIMARY KEY,
    data TEXT
);
""")
pg_conn.commit()

my_cur.execute("""
CREATE TABLE IF NOT EXISTS test_sync (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data TEXT
);
""")
my_conn.commit()

pg_cur.close()
pg_conn.close()
my_cur.close()
my_conn.close()
