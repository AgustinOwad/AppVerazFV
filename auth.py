# auth.py
import sqlite3
import hashlib

def verificar_credenciales(usuario, contrasena):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash, rol FROM usuarios WHERE LOWER(username) = ?", (usuario.lower(),))
    row = cursor.fetchone()
    conn.close()

    if row:
        username, stored_hash, rol = row
        hash_input = hashlib.sha256(contrasena.encode()).hexdigest()
        if stored_hash == hash_input:
            return username, rol
    return None, None
