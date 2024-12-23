import os
import sqlite3
import pandas as pd
from datetime import datetime  # Para generar la marca de tiempo

# Ruta donde están las bases de datos
DATABASES_DIR = "D:/Inventory/databases"
DB_SUFFIX = "_inventory.db"  # Sufijo de las bases de datos

def get_timestamp():
    """Genera una marca de tiempo para los nombres de archivo."""
    return datetime.now().strftime("%d%m%Y_%H%M%S")  # Formato: DDMMYYYY_HHMMSS

def export_database_to_excel():
    # Solicitar al usuario el nombre base de la base de datos
    db_name = input(f"Ingrese el nombre de la base de datos (sin '{DB_SUFFIX}'): ")
    db_path = os.path.join(DATABASES_DIR, f"{db_name}{DB_SUFFIX}")
    
    # Verificar si la base de datos existe
    if not os.path.exists(db_path):
        print(f"La base de datos '{db_name}{DB_SUFFIX}' no existe en {DATABASES_DIR}.")
        return

    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    table_name = "inventory"  # Cambiar si la tabla tiene otro nombre
    
    try:
        # Intentar leer los datos de la tabla
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # Generar el nombre del archivo con la marca de tiempo
        timestamp = get_timestamp()
        export_path = os.path.join(DATABASES_DIR, f"{db_name}_export_{timestamp}.xlsx")
        
        # Exportar a Excel
        df.to_excel(export_path, index=False)
        print(f"Datos exportados exitosamente a: {export_path}")
    except Exception as e:
        print(f"Error al exportar los datos: {e}")
    finally:
        conn.close()

# Ejecutar el script
if __name__ == "__main__":
    export_database_to_excel()
