import psycopg2

conn = psycopg2.connect(dbname='didi_db', user='odoo', password='odoo', host='localhost', port=5433)
cur = conn.cursor()

# Delete stale views for shop.order
cur.execute("DELETE FROM ir_ui_view WHERE model = 'shop.order'")
print(f"Deleted {cur.rowcount} ir_ui_view records for shop.order")

# Delete stale views for shop.order.line
cur.execute("DELETE FROM ir_ui_view WHERE model = 'shop.order.line'")
print(f"Deleted {cur.rowcount} ir_ui_view records for shop.order.line")

# Delete all ir_model_data for shop_manager module
cur.execute("DELETE FROM ir_model_data WHERE module = 'shop_manager'")
print(f"Deleted {cur.rowcount} ir_model_data records for shop_manager")

# Delete ir_act_report_xml for shop_manager
cur.execute("DELETE FROM ir_act_report_xml WHERE report_name LIKE 'shop_manager.%'")
print(f"Deleted {cur.rowcount} ir_act_report_xml records")

# Reset module state to uninstalled
cur.execute("UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'shop_manager'")
print(f"Updated {cur.rowcount} module records to uninstalled")

conn.commit()
print("Cleanup done!")
cur.close()
conn.close()
