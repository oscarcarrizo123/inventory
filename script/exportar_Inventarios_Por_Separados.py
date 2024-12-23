import sqlite3
import os
from openpyxl import Workbook
from datetime import datetime

# Ruta donde están almacenadas las bases de datos
db_folder = r'D:/Inventory/databases/'
output_folder = r'D:/Inventory/databases/inventarios_separados/'

# Crear la carpeta de salida si no existe
os.makedirs(output_folder, exist_ok=True)

# Lista de las bases de datos
databases = [
    'admin_inventory.db',
    'Oscar_inventory.db',
    'Albaro_inventory.db',
    'Antonella_inventory.db',
    'Selva_inventory.db',
    'Nahuel_inventory.db',
    'Sebastian_inventory.db',
    'Rodrigo_inventory.db',
    'Nestor_inventory.db',
    'Jose_inventory.db',
    'Raul_inventory.db'
]

# Función para generar una marca de tiempo única
def get_timestamp():
    return datetime.now().strftime("%d%m%Y_%H%M%S")  # Formato: DDMMYYY_HHMMSS

# Función para exportar datos de una base de datos directamente a Excel
def export_database_to_excel(db_name, db_path):
    try:
        # Conexión a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar si la tabla inventory existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory'")
        if not cursor.fetchone():
            print(f"La base de datos {db_name} no tiene una tabla 'inventory'.")
            return

        # Crear el archivo Excel con marca de tiempo
        timestamp = get_timestamp()
        output_excel = os.path.join(output_folder, f"{db_name.replace('.db', '')}_{timestamp}.xlsx")
        wb = Workbook()
        ws = wb.active
        ws.title = "Inventario"

        # Escribir encabezados
        ws.append(['ID', 'Sector', 'Código de Barras', 'Descripción', 'Presentación', 'Tipo', 'Cantidad'])

        # Escribir filas de datos
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        for row in rows:
            ws.append(row)

        # Guardar el archivo Excel
        wb.save(output_excel)
        print(f"Datos exportados a {output_excel}")

    except Exception as e:
        print(f"Error procesando la base {db_name}: {e}")

    finally:
        conn.close()

# Exportar todas las bases de datos
for db in databases:
    db_path = os.path.join(db_folder, db)
    if os.path.exists(db_path):
        export_database_to_excel(db, db_path)
    else:
        print(f"La base de datos {db} no existe en la ruta especificada.")
