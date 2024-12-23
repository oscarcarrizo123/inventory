from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Ruta base para las bases de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOLDER = os.path.join(BASE_DIR, 'databases')
os.makedirs(DB_FOLDER, exist_ok=True)

# Crear la base de datos general para usuarios
global_db_path = os.path.join(BASE_DIR, 'users.db')
with sqlite3.connect(global_db_path) as conn:
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    conn.commit()

def create_user_database(username):
    db_path = os.path.join(DB_FOLDER, f"{username}_inventory.db")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector TEXT NOT NULL,
            barcode TEXT NOT NULL,
            description TEXT NOT NULL,
            presentation TEXT NOT NULL,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
        ''')
        conn.commit()
    return db_path

@app.route('/admin')
def admin():
    if 'username' not in session or session.get('username') != 'admin':
        return "Acceso denegado.", 403

    try:
        with sqlite3.connect(global_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users")
            users = [{"id": row[0], "username": row[1]} for row in cursor.fetchall()]

        return render_template('admin.html', users=users)
    except Exception as e:
        return str(e), 500

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' not in session or session.get('username') != 'admin':
        return "Acceso denegado.", 403

    try:
        with sqlite3.connect(global_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()

        return jsonify({"message": "Usuario eliminado correctamente."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        with sqlite3.connect(global_db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                create_user_database(username)
                return "Usuario agregado exitosamente."
            except sqlite3.IntegrityError:
                return "El usuario ya existe."
    return render_template('add_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']

        with sqlite3.connect(global_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, password FROM users WHERE LOWER(username) = ?', (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['username'] = username
                session['db_path'] = os.path.join(DB_FOLDER, f"{username}_inventory.db")
                return redirect(url_for('home'))
            else:
                error = "Usuario o contraseña incorrectos."
                return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/get_inventory', methods=['GET'])
def get_inventory():
    if 'db_path' not in session:
        return redirect(url_for('login'))

    db_path = session['db_path']
    try:
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"La base de datos no existe en la ruta: {db_path}")

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM inventory ORDER BY id DESC')
            rows = cursor.fetchall()
            inventory = [
                {
                    "id": row[0],
                    "sector": row[1],
                    "barcode": row[2],
                    "description": row[3],
                    "presentation": row[4],
                    "type": row[5],
                    "quantity": row[6]
                } for row in rows
            ]
        return jsonify(inventory)
    except FileNotFoundError as fnf_error:
        return jsonify({"error": str(fnf_error)}), 404
    except Exception as e:
        return jsonify({"error": f"No se pudo cargar el inventario: {str(e)}"}), 500

products_db_path = os.path.join(BASE_DIR, 'products.db')

@app.route('/get_product/<barcode>', methods=['GET'])
def get_product(barcode):
    try:
        if not os.path.exists(products_db_path):
            raise FileNotFoundError("La base de datos de productos no existe.")

        with sqlite3.connect(products_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT description, presentation, type FROM products WHERE barcode = ?', (barcode,))
            product = cursor.fetchone()
            if product:
                return jsonify({
                    "description": product[0],
                    "presentation": product[1],
                    "type": product[2]
                })
            else:
                return jsonify({"error": "Producto no encontrado."}), 404
    except FileNotFoundError as fnf_error:
        return jsonify({"error": str(fnf_error)}), 404
    except Exception as e:
        return jsonify({"error": f"Error al buscar el producto: {str(e)}"}), 500

@app.route('/add_item', methods=['POST'])
def add_item():
    if 'db_path' not in session:
        return jsonify({"error": "Usuario no autenticado."}), 401

    db_path = session['db_path']
    data = request.get_json()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO inventory (sector, barcode, description, presentation, type, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['sector'],
                data['barcode'],
                data['description'],
                data['presentation'],
                data['type'],
                data['quantity']
            ))
            conn.commit()
            new_item_id = cursor.lastrowid

        return jsonify({
            "message": "Item agregado correctamente.",
            "item": {
                "id": new_item_id,
                "sector": data['sector'],
                "barcode": data['barcode'],
                "description": data['description'],
                "presentation": data['presentation'],
                "type": data['type'],
                "quantity": data['quantity']
            }
        }), 201

    except Exception as e:
        return jsonify({"error": f"Error al agregar el ítem: {str(e)}"}), 500

@app.route('/edit_item/<int:item_id>', methods=['PUT'])
def edit_item(item_id):
    if 'db_path' not in session:
        return redirect(url_for('login'))

    db_path = session['db_path']
    data = request.get_json()
    quantity = data.get('quantity')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE inventory
        SET quantity = ?
        WHERE id = ?
        ''', (quantity, item_id))
        conn.commit()

    return jsonify({"message": "Cantidad actualizada correctamente."})

@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if 'db_path' not in session:
        return redirect(url_for('login'))

    db_path = session['db_path']
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
        conn.commit()

    return jsonify({"message": "Item eliminado correctamente."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Usar el puerto de Render o 5000 como predeterminado
    app.run(host='0.0.0.0', port=port)
