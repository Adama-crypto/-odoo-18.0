import psycopg2

conn = psycopg2.connect(dbname='test_it_parc', user='odoo', password='odoo', host='localhost', port=5433)
cur = conn.cursor()

# Get all tables
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
""")
tables = [row[0] for row in cur.fetchall()]

found = False

for table in tables:
    try:
        # Check if table has 'id' column
        cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = 'id'
        """, (table,))
        if not cur.fetchone():
            continue
            
        cur.execute(f"SELECT * FROM \"{table}\" WHERE id = 14")
        rows = cur.fetchall()
        if rows:
            print(f"Found id=14 in table '{table}':")
            for row in rows:
                print(row)
            found = True
    except Exception as e:
        conn.rollback()

if not found:
    print("ID 14 not found in any table.")

cur.close()
conn.close()
