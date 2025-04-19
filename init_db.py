# init_db.py
import sqlite3
import hashlib

# Conectar a la DB (si no existe, se crea en la ruta actual)
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Si deseas un reinicio (solo en desarrollo), opcionalmente eliminar la tabla anterior:
cursor.execute("DROP TABLE IF EXISTS usuarios")

# Crear la tabla usuarios
cursor.execute("""
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL
)
""")

# Función para hashear la contraseña
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# Insertar usuarios iniciales
usuarios_iniciales = [
    ("Admin", hash_pw("Cabj1905!!"), "admin"),
    ("Fran", hash_pw("Filipenses413"), "admin"),
    ("fvlawfirm", hash_pw("Filipenses413"), "usuario")
]

for user, pw_hash, rol in usuarios_iniciales:
    try:
        cursor.execute("INSERT INTO usuarios (username, password_hash, rol) VALUES (?, ?, ?)",
                       (user, pw_hash, rol))
    except sqlite3.IntegrityError:
        # En caso de que ya exista, puedes optar por ignorar o mostrar un mensaje.
        print(f"El usuario {user} ya existe, omitiendo...")

conn.commit()
conn.close()

print("Base de datos 'usuarios.db' creada y actualizada correctamente.")
