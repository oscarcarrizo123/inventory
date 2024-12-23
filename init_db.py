import sqlite3
from werkzeug.security import generate_password_hash

# Nombre de la base de datos
db_path = 'users.db'

# Conexión a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla de usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Generar el hash de la contraseña para 'admin'
password_hash = generate_password_hash('admin123')

# Insertar el usuario admin
try:
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', password_hash))
    conn.commit()
    print("Usuario admin creado exitosamente.")
except sqlite3.IntegrityError:
    print("El usuario admin ya existe.")

conn.close()
