import psycopg2

conn = psycopg2.connect(dbname='test_it_parc', user='odoo', password='odoo', host='localhost', port=5433)
cur = conn.cursor()

print("=== CUSTOM/MANUAL MODELS ===")
try:
    cur.execute("SELECT id, model, name, state FROM ir_model WHERE state = 'manual'")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print("Error ir_model:", e)
    conn.rollback()

print("\n=== MODELS CONTAINING PC OR PORTABLE ===")
try:
    cur.execute("SELECT id, model, name, state FROM ir_model WHERE model LIKE '%PC%' OR model LIKE '%port%' OR model LIKE '%PORT%'")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print("Error ir_model query:", e)
    conn.rollback()

cur.close()
conn.close()
