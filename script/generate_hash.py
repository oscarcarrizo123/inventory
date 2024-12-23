from werkzeug.security import generate_password_hash

# Cambia 'tu_contraseña' por la que quieras generar
password = 'ciudadela'
print(generate_password_hash(password))
