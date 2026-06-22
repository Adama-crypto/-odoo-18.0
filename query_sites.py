import psycopg2

conn = psycopg2.connect(dbname='test_it_parc', user='odoo', password='odoo', host='localhost', port=5433)
cur = conn.cursor()

print("=== IT SITES ===")
try:
    cur.execute("SELECT id, name FROM it_site")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print("Error it_site:", e)
    conn.rollback()

cur.close()
conn.close()
