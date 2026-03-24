from passlib.context import CryptContext
import pyodbc

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_existing_users():
    conn_str = (
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=.\SQLEXPRESS;'                     
        r'DATABASE=LIBRARY;'
        r'Trusted_Connection=yes;'                  
        r'Encrypt=no;'
        r'Connection Timeout=10;'
    )
    try:
        conn = pyodbc.connect(conn_str)
        print("Conexión exitosa (autenticación Windows)")
    except pyodbc.Error as ex:
        print("Error:")
        print(ex)
        exit(1)

    cursor = conn.cursor()

    users_to_update = [
        (1, 'Admin2024!'),
        (2, 'Carlos789*'),
        (3, 'D14n4_2024'),
        (4, 'Cuentos123'),
        (5, 'HadaMadrina'),
        (6, 'Goleador09'),
        (7, 'OroOlimpico'),
        (8, 'DinoRwar'),
    ]

    for user_id, plain in users_to_update:
        hashed = pwd_context.hash(plain)
        cursor.execute("UPDATE Usuarios SET Contraseña = ? WHERE Id = ?", (hashed, user_id))
        print(f"ID {user_id} actualizado" if cursor.rowcount == 1 else f"ID {user_id} no encontrado")

    conn.commit()
    conn.close()

    print("Proceso terminado.")
    return True

if __name__ == "__main__":
    hash_existing_users()