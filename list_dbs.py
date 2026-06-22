import psycopg2

try:
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost', port=5433)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
    dbs = [row[0] for row in cur.fetchall()]
    print("Databases:", dbs)
    cur.close()
    conn.close()
except Exception as e:
    print("Error listing databases:", e)
