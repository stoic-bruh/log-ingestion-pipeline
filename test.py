import psycopg2

try:
    conn = psycopg2.connect(
        dbname="logs_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )
    print("CONNECTED SUCCESSFULLY")
except Exception as e:
    print("ERROR:", e)