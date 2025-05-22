import psycopg2

try:
    conn = psycopg2.connect(
        dbname="your_db_name",
        user="your_db_user",
        password="your_password",
        host="localhost",
        port="5432"
    )
    print("✅ PostgreSQL connection successful!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
