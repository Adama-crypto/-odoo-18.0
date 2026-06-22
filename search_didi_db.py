import psycopg2

try:
    conn = psycopg2.connect(dbname='didi_db', user='odoo', password='odoo', host='localhost', port=5433)
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    target = '%PC-PORTABLE-DIR-01%'
    found = False
    
    for table in tables:
        try:
            # Get text columns of the table
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND data_type IN ('character varying', 'text')
            """, (table,))
            columns = [row[0] for row in cur.fetchall()]
            if not columns:
                continue
            
            # Construct query to search for the value in these columns
            conditions = [f"LOWER(\"{col}\") LIKE LOWER(%s)" for col in columns]
            query = f"SELECT * FROM \"{table}\" WHERE " + " OR ".join(conditions)
            cur.execute(query, tuple(target for _ in columns))
            rows = cur.fetchall()
            if rows:
                print(f"Found in didi_db table '{table}':")
                for row in rows:
                    print(row[:5])
                found = True
        except Exception as e:
            conn.rollback()
            
    if not found:
        print("Not found in didi_db.")
        
    cur.close()
    conn.close()
except Exception as e:
    print("Could not connect to didi_db:", e)
