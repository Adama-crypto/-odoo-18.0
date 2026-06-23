# it_parc Odoo 18 Module

## Overview
`it_parc` is a fully‑featured Odoo 18 module for **Gestion du Parc Informatique** developed for TECHPARK CI. It provides:
- Asset management (PCs, servers, printers, network devices, IP phones)
- Assignment tracking, maintenance interventions, supplier contracts
- Automatic alerts on warranties and contract expirations
- CSV bulk import, PDF reports and Excel exports
- A modern OWL Dashboard with **4 KPIs** and a **category bar chart**

---

## Prerequisites
- **Odoo 18** installed (see Odoo documentation for installation steps)
- Python 3.11+ and a virtual environment
- PostgreSQL 13+ database
- `xlsxwriter` Python package (required for Excel exports)

## Installation
1. **Clone or download the repository**
   ```bash
   git clone https://github.com/your‑org/it_parc.git
   cd it_parc
   ```
2. **Copy the module into your Odoo addons directory**
   ```bash
   # assuming your Odoo addons path is ./addons
   cp -R addons/it_parc <YOUR_ODOO_ADDONS_PATH>/it_parc
   ```
3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Update Odoo configuration** (`odoo.conf`) to include the addons path if not already present:
   ```ini
   [options]
   addons_path = <YOUR_ODOO_ADDONS_PATH>
   ```
5. **Start Odoo and install the module**
   ```bash
   python odoo-bin -c odoo.conf -d <YOUR_DB_NAME> -u it_parc
   ```
   - After the server starts, go to *Apps* → search **IT Parc** → click **Install**.

---

## Loading Demo Data (Zero‑Click Demo)
The module ships a demo XML file `it_parc_demo.xml` that creates:
- 10 sample equipments
- 3 contracts, 5 interventions, 2 suppliers
- Users and groups required for the dashboard

To load the demo data:
```bash
python odoo-bin -c odoo.conf -d <YOUR_DB_NAME> -i it_parc_demo
```
Or from the UI: *Apps* → *Update Apps List* → enable **Technical Features**, then go to *Apps* → *IT Parc* → click **Load Demo Data**.

---

## PDF Reports & Excel Exports
### PDF Reports
- **Inventaire**: *IT → Inventaire → Imprimer PDF*
- **Maintenance**: *IT → Maintenance → Imprimer PDF*
- **Équipement**: *IT → Équipements → Imprimer PDF*

The reports are defined in `report/it_*.xml` and use Odoo QWeb. No extra configuration is required.

### Excel Exports
Two actions are available from the list view buttons:
- **Export Inventaire** → generates `inventaire_<date>.xlsx`
- **Export Coûts Maintenance** → generates `couts_maintenance_<date>.xlsx`
- **Export Contrats Expirants** → generates `contrats_expirants_<date>.xlsx`

The files are stored as `ir.attachment` and automatically downloaded by the browser.

---

## Dashboard
The OWL dashboard is reachable via the menu **IT → Dashboard**.
It shows four KPIs:
1. **Total Équipements**
2. **Équipements Affectés**
3. **En Maintenance**
4. **Interventions en cours**

And two visualisations:
- **Équipements par catégorie** (horizontal progress bars)
- **Interventions par mois** (last 6 months bar chart)

No additional configuration is needed; the data is fetched from the RPC endpoint `/it_parc/dashboard/data`.

---

## Development & Testing
- Run unit tests:
  ```bash
  python odoo-bin -c odoo.conf -d test_it_parc --test-enable -u it_parc --stop-after-init
  ```
- Lint the Python code with `flake8` (optional).

---

## License
This module is released under the **LGPL‑3** license (see the `LICENSE` file).

---

## Contact
Developed by **TECHPARK CI** – 2024‑2025.
For support, contact `contact@techpark-solutions.ci`.
