import os

root_dir = r"c:\Users\MSI\Downloads\odoo-18.0\odoo-18.0"
target = "PC-PORTABLE-DIR-01"
found = False

for dirpath, dirnames, filenames in os.walk(root_dir):
    # Skip some heavy directories like .git
    if '.git' in dirpath:
        continue
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if target in content:
                    print(f"Found in file: {file_path}")
                    found = True
        except Exception as e:
            pass

if not found:
    print("Not found in any file.")
