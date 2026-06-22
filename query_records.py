import psycopg2

conn = psycopg2.connect(dbname='test_it_parc', user='odoo', password='odoo', host='localhost', port=5433)
cur = conn.cursor()

# Get all equipments
print("=== IT EQUIPEMENTS ===")
try:
    cur.execute("SELECT id, name, numero_serie, state FROM it_equipement")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print("Error it_equipement:", e)
    conn.rollback()

print("\n=== IT CATEGORIES ===")
try:
    cur.execute("SELECT id, name, code, description FROM it_equipement_categorie")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print("Error it_equipement_categorie:", e)
    conn.rollback()

cur.close()
conn.close()
