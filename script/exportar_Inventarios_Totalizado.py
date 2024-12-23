import sqlite3
import os
from openpyxl import Workbook
from datetime import datetime

# Ruta donde están almacenadas las bases de datos
db_folder = os.path.join(os.getcwd(), 'databases')
output_folder = os.path.join(os.getcwd(), 'databases', 'inventario_totalizado')

# Crear la carpeta de salida si no existe
os.makedirs(output_folder, exist_ok=True)

# Lista de las bases de datos
databases = [
    'albaro_inventory.db',
    'antonella_inventory.db',
    'selva_inventory.db',
    'nahuel_inventory.db',
    'sebastian_inventory.db',
    'rodrigo_inventory.db',
    'nestor_inventory.db',
    'jose_inventory.db',
    'raul_inventory.db',
    'oscar_inventory.db'
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
        SELECT 'Albaro', * FROM albaro_inventory.inventory
        UNION ALL
        SELECT 'Antonella', * FROM antonella_inventory.inventory
        UNION ALL
        SELECT 'Selva', * FROM selva_inventory.inventory
        UNION ALL
        SELECT 'Nahuel', * FROM nahuel_inventory.inventory
        UNION ALL
        SELECT 'Sebastian', * FROM sebastian_inventory.inventory
        UNION ALL
        SELECT 'Rodrigo', * FROM rodrigo_inventory.inventory
        UNION ALL
        SELECT 'Nestor', * FROM nestor_inventory.inventory
        UNION ALL
        SELECT 'Jose', * FROM jose_inventory.inventory
        UNION ALL
        SELECT 'Raul', * FROM raul_inventory.inventory
        UNION ALL
        SELECT 'Oscar', * FROM oscar_inventory.inventory
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

# Confirmación final
file_name = f"inventario_totalizado_{datetime.now().strftime('%d%m%Y_%H%M%S')}.xlsx"
file_path = os.path.join(output_folder, file_name)
print(f"Archivo Excel generado en: {file_path}")
