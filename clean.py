# clean_database.py
import json
import os

def clean_database():
    """Limpia la base de datos JSON"""
    data_file = "invoices_data.json"
    
    if os.path.exists(data_file):
        # Hacer backup por si acaso
        backup_file = f"invoices_data_backup_{os.path.getmtime(data_file)}.json"
        os.rename(data_file, backup_file)
        print(f"✅ Backup creado: {backup_file}")
    
    # Crear archivo vacío
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump({}, f, indent=2)
    
    print("🗑️  Base de datos limpiada exitosamente")
    return True

if __name__ == "__main__":
    clean_database()