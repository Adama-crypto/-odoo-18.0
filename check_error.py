#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import odoo
odoo.tools.config.parse_config(['--config=odoo.conf'])
from odoo.modules.registry import Registry
from odoo import api, SUPERUSER_ID

reg = Registry('test_it_parc')
with reg.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check action 506
    print("=== Action with xmlid or id around 506 ===")
    cr.execute("SELECT id, name, res_model, type FROM ir_act_window WHERE id = 506")
    for row in cr.fetchall():
        print(f"  act_window: {row}")
    
    cr.execute("SELECT id, name, type FROM ir_actions WHERE id = 506")
    for row in cr.fetchall():
        print(f"  actions: {row}")
    
    # Check record id=14 in it.intervention
    print("\n=== it.intervention id=14 ===")
    try:
        inter = env['it.intervention'].browse(14)
        print(f"  name={inter.name}")
        print(f"  equipement={inter.equipement_id.name}")
        print(f"  state={inter.state}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Check all interventions
    print("\n=== All interventions ===")
    inters = env['it.intervention'].search([])
    for i in inters:
        print(f"  id={i.id} name='{i.name}' equipement='{i.equipement_id.name}' state={i.state}")
    
    # Look for 'PC-PORTABLE' anywhere in the DB
    print("\n=== Search PC-PORTABLE in all text columns ===")
    cr.execute("""
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND data_type IN ('character varying', 'text')
        AND table_name IN ('it_equipement', 'it_intervention', 'it_affectation', 'it_contrat', 'it_alerte')
    """)
    cols = cr.fetchall()
    for table, col in cols:
        cr.execute(f"SELECT id, {col} FROM {table} WHERE {col}::text ILIKE '%PC-PORTABLE%'")
        rows = cr.fetchall()
        if rows:
            print(f"  FOUND in {table}.{col}: {rows}")
