import os
import sys
import psycopg2
from decouple import config

try:
    DB_NAME = config('SUPABASE_DB_NAME')
    DB_USER = config('SUPABASE_DB_USER')
    DB_PASSWORD = config('SUPABASE_DB_PASSWORD')
    DB_HOST = config('SUPABASE_DB_HOST')
    DB_PORT = config('SUPABASE_DB_PORT', default='6543')

    print(f"Attempting to connect to database: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        sslmode='require',
        connect_timeout=10
    )
    cur = conn.cursor()
    cur.execute("SELECT 1")
    cur.close()
    conn.close()
    print("Database connection successful!")
    sys.exit(0)
except Exception as e:
    print(f"Database connection failed: {e}", file=sys.stderr)
    sys.exit(1)
