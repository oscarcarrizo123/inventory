import sqlite3
import os
import shutil
from datetime import datetime

# Ruta donde están las bases de datos
DATABASES_DIR = "D:/Inventory/databases"
DB_SUFFIX = "_inventory.db"  # Sufijo de las bases de datos
BACKUP_DIR = "D:/Inventory/databases/backups"  # Carpeta raíz para guardar los backups

# Crear la carpeta raíz de backups si no existe
os.makedirs(BACKUP_DIR, exist_ok=True)

# Función para generar un backup
def create_backup(db_name):
    db_path = os.path.join(DATABASES_DIR, f"{db_name}{DB_SUFFIX}")
    if os.path.exists(db_path):
        # Crear una subcarpeta para la base de datos
        subfolder = os.path.join(BACKUP_DIR, db_name)
        os.makedirs(subfolder, exist_ok=True)

        # Crear un nombre único para el backup con fecha y hora
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        backup_path = os.path.join(subfolder, f"{db_name}_{timestamp}.db")

        # Copiar el archivo de la base de datos al directorio de backup
        shutil.copy(db_path, backup_path)
        print(f"Backup creado en: {backup_path}")
    else:
        print(f"La base de datos '{db_name}{DB_SUFFIX}' no existe. No se puede generar el backup.")

# Función para limpiar los datos de una base de datos específica
def clear_database(db_name):
    db_path = os.path.join(DATABASES_DIR, f"{db_name}{DB_SUFFIX}")

    # Verificar si la base de datos existe
    if not os.path.exists(db_path):
        print(f"La base de datos '{db_name}{DB_SUFFIX}' no existe en {DATABASES_DIR}.")
        return

    try:
        # Crear un backup antes de limpiar
        create_backup(db_name)

        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar si la tabla inventory existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory'")
        if not cursor.fetchone():
            print(f"La base de datos {db_name} no tiene una tabla 'inventory'.")
            return

        # Eliminar todos los datos de la tabla inventory
        cursor.execute("DELETE FROM inventory")
        conn.commit()
        print(f"Todos los datos de la tabla 'inventory' en {db_name} fueron eliminados.")

    except Exception as e:
        print(f"Error al limpiar la base de datos {db_name}: {e}")

    finally:
        conn.close()

# Función para limpiar los datos de todas las bases de datos
def clear_all_databases():
    for db_file in os.listdir(DATABASES_DIR):
        if db_file.endswith(DB_SUFFIX):
            db_name = db_file.replace(DB_SUFFIX, "")
            clear_database(db_name)

# Menú de opciones
def main():
    print("Opciones:")
    print("1. Limpiar una base de datos específica (con backup)")
    print("2. Limpiar todas las bases de datos (con backup)")
    choice = input("Seleccione una opción (1 o 2): ")

    if choice == "1":
        db_name = input("Ingrese el nombre de la base de datos (sin el sufijo '_inventory'): ")
        clear_database(db_name)
    elif choice == "2":
        confirm = input("¿Está seguro de que desea limpiar todas las bases de datos? (sí/no): ")
        if confirm.lower() == "sí":
            clear_all_databases()
        else:
            print("Operación cancelada.")
    else:
        print("Opción no válida.")

# Ejecutar el script
if __name__ == "__main__":
    main()
