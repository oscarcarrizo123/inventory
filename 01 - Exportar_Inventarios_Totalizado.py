import sqlite3
import os
from openpyxl import Workbook
from datetime import datetime

# Ruta donde están almacenadas las bases de datos
db_folder = r'D:\Inventory\databases'
output_folder = r'D:/Inventory/databases/inventario_totalizado/'

# Crear la carpeta de salida si no existe
os.makedirs(output_folder, exist_ok=True)

# Lista de las bases de datos
databases = [
    'Albaro_inventory.db',
    'Antonella_inventory.db',
    'Selva_inventory.db',
    'Nahuel_inventory.db',
    'Sebastian_inventory.db',
    'Rodrigo_inventory.db',
    'Nestor_inventory.db',
    'Jose_inventory.db',
    'Raul_inventory.db',
    'Oscar_inventory.db'
]

# Función para exportar datos totalizados a Excel
def export_totalized_inventory_to_excel():
    try:
        print("Iniciando la exportación directamente a Excel...")
        # Conexión a múltiples bases de datos y consolidación de datos
        conn = sqlite3.connect(':memory:')  # Base de datos en memoria para combinar
        cursor = conn.cursor()

        for db_name in databases:
            db_path = os.path.join(db_folder, db_name)
            if os.path.exists(db_path):
                attach_name = db_name.replace('.db', '')
                print(f"Conectando base de datos: {db_name}")
                cursor.execute(f"ATTACH DATABASE '{db_path}' AS {attach_name}")
            else:
                print(f"Base de datos no encontrada: {db_name}")

        # Crear una vista consolidada de inventarios
        cursor.execute('''
        CREATE TEMP VIEW total_inventory AS
        SELECT 'Albaro', * FROM Albaro_inventory.inventory
        UNION ALL
        SELECT 'Antonella', * FROM Antonella_inventory.inventory
        UNION ALL
        SELECT 'Selva', * FROM Selva_inventory.inventory
        UNION ALL
        SELECT 'Nahuel', * FROM Nahuel_inventory.inventory
        UNION ALL
        SELECT 'Sebastian', * FROM Sebastian_inventory.inventory
        UNION ALL
        SELECT 'Rodrigo', * FROM Rodrigo_inventory.inventory
        UNION ALL
        SELECT 'Nestor', * FROM Nestor_inventory.inventory
        UNION ALL
        SELECT 'Jose', * FROM Jose_inventory.inventory
        UNION ALL
        SELECT 'Raul', * FROM Raul_inventory.inventory
        UNION ALL
        SELECT 'Oscar', * FROM Oscar_inventory.inventory
        ''')
        print("Vista consolidada creada correctamente.")

        # Crear el archivo Excel
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        output_excel = os.path.join(output_folder, f"inventario_totalizado_{timestamp}.xlsx")

        wb = Workbook()
        ws = wb.active
        ws.title = "Inventario Totalizado"

        # Escribir encabezados
        ws.append(['Base', 'ID', 'Sector', 'Código de Barras', 'Descripción', 'Presentación', 'Tipo', 'Cantidad'])

        # Escribir filas de datos
        cursor.execute("SELECT * FROM total_inventory")
        rows = cursor.fetchall()
        for row in rows:
            ws.append(row)

        # Guardar el archivo Excel
        wb.save(output_excel)
        print(f"Inventario totalizado exportado a {output_excel}")

    except Exception as e:
        print(f"Error procesando el inventario totalizado: {e}")

    finally:
        conn.close()

# Ejecutar exportación totalizada
export_totalized_inventory_to_excel()
