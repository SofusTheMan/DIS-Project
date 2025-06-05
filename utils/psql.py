import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()

psql_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT"))
)

def psql(query):
    print(f"Executing query: {query}")
    conn = psql_pool.getconn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query)
    conn.commit()
    data = None
    try:
        data = cur.fetchall()
    except:
        pass
    cur.close()
    psql_pool.putconn(conn)
    return data