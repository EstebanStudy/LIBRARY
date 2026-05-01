import pytest
import sys
from pathlib import Path

# ==================== CONFIGURACIÓN CORRECTA DE RUTAS ====================
root_path = Path(__file__).parent.parent  # Apunta a LIBRARY/
sys.path.insert(0, str(root_path / "Backend"))   # ← Esto es lo más importante

# Ahora sí podemos importar desde Backend
from main import app

from fastapi.testclient import TestClient

client = TestClient(app)

# ==================== INSTRUCCIONES PARA POSTMAN ====================
# Para replicar estas pruebas en Postman:
# 1. Configura una variable de entorno "base_url" con el valor: http://127.0.0.1:8000
# 2. Crea variables para tokens: admin_token, user_token, nino_token
# 3. Ejecuta primero los logins para obtener los tokens y asignarlos a las variables
# 4. Usa las variables en los headers: Authorization: Bearer {{admin_token}}
# 5. Cada prueba incluye detalles POSTMAN con método, URL, headers y body esperados
# ==================== FIN INSTRUCCIONES ====================

# ==================== FIXTURES ====================

@pytest.fixture(scope="module")
def admin_token():
    response = client.post(
        "/auth/login",
        data={"username": "betty.admin@library.com", "password": "Admin2024!"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def nino_token():
    response = client.post(
        "/auth/login",
        data={"username": "kevin.kids@library.com", "password": "Cuentos123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def user_token():
    response = client.post(
        "/auth/login",
        data={"username": "carlos.lector@gmail.com", "password": "Carlos789*"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

# ==================== AUTHENTICATION TESTS (TC-01, TC-07, TC-13, TC-18) ====================

def test_01_login_admin_ok():
    """
    TC-01 | US-05 | Equivalencia (válido) | Login correcto de administrador

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/auth/login
    - Headers: Content-Type: application/x-www-form-urlencoded
    - Body (form-data):
        username: betty.admin@library.com
        password: Admin2024!
    - Expected: 200 OK, response with access_token and role: Administrador
    """
    response = client.post("/auth/login", data={"username": "betty.admin@library.com", "password": "Admin2024!"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["role"] == "Administrador"

def test_07_login_credenciales_incorrectas():
    """
    TC-13 | US-05 | Equivalencia (inválido) | Login con contraseña errónea

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/auth/login
    - Headers: Content-Type: application/x-www-form-urlencoded
    - Body (form-data):
        username: betty.admin@library.com
        password: mala
    - Expected: 401 Unauthorized
    """
    response = client.post("/auth/login", data={"username": "betty.admin@library.com", "password": "mala"})
    assert response.status_code == 401

def test_12_register_correo_duplicado():
    """
    TC-18 | US-05 | Equivalencia (inválido) | Registrar con correo ya usado

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/auth/register
    - Headers: Content-Type: application/json
    - Body (raw JSON):
        {
            "Cod_usuario": 1001,
            "Correo": "betty.admin@library.com",
            "Contraseña": "Test12345",
            "Persona": 1,
            "Rol": 1
        }
    - Expected: 400 Bad Request, message containing "Correo ya registrado"
    """
    data = {
        "Cod_usuario": 1001,
        "Correo": "betty.admin@library.com",
        "Contraseña": "Test12345",
        "Persona": 1,
        "Rol": 1
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert "Correo ya registrado" in response.json().get("detail", "")

# ==================== BOOKS TESTS (TC-02, TC-03, TC-19, TC-20, TC-21) ====================

def test_02_create_libro_codigo_duplicado(admin_token):
    """
    TC-02 | US-01 | Equivalencia (inválido) | Crear libro con código duplicado

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/libros/
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Cod_libro": 5001,
            "Nombre_libro": "Libro Duplicado",
            "Autor": "Test"
        }
    - Expected: 400 Bad Request, message about código duplicado
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Cod_libro": 5001, "Nombre_libro": "Libro Duplicado", "Autor": "Test"}
    response = client.post("/libros/", json=data, headers=headers)
    assert response.status_code == 400
    assert "código" in response.json()["detail"].lower() or "existe" in response.json()["detail"].lower()

def test_03_get_libros_paginados(admin_token):
    """
    TC-03 | US-01 | Exhaustividad | Leer libros con paginación (skip=0, limit=5)

    POSTMAN:
    - Method: GET
    - URL: {{base_url}}/libros/?skip=0&limit=5
    - Headers: Authorization: Bearer {{admin_token}}
    - Body: None
    - Expected: 200 OK, array with <=5 libros
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/libros/?skip=0&limit=5", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) <= 5

def test_13_update_libro_codigo_duplicado(admin_token):
    """
    TC-19 | US-01 | Decisión | Actualizar libro con código ya existente

    POSTMAN:
    - Method: PUT
    - URL: {{base_url}}/libros/{{libro_id}} (crear uno temporal primero)
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Cod_libro": 5001,
            "Nombre_libro": "Actualizado"
        }
    - Expected: 400 Bad Request, message about código duplicado
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Cod_libro": 7777, "Nombre_libro": "Temporal", "Autor": "Test"}
    resp = client.post("/libros/", json=data, headers=headers)
    assert resp.status_code == 201
    libro_id = resp.json()["Id"]

    update_data = {"Cod_libro": 5001, "Nombre_libro": "Actualizado"}
    response = client.put(f"/libros/{libro_id}", json=update_data, headers=headers)
    assert response.status_code == 400
    assert "código" in response.json()["detail"].lower() or "existe" in response.json()["detail"].lower()

    client.delete(f"/libros/{libro_id}", headers=headers)

def test_15_eliminar_libro_existente(admin_token):
    """
    Caso extra: Eliminar libro correctamente

    POSTMAN:
    - Method: DELETE
    - URL: {{base_url}}/libros/{{libro_id}} (crear uno temporal)
    - Headers: Authorization: Bearer {{admin_token}}
    - Body: None
    - Expected: 200 OK, luego GET 404
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Cod_libro": 8888, "Nombre_libro": "ParaEliminar", "Autor": "Test"}
    resp = client.post("/libros/", json=data, headers=headers)
    assert resp.status_code == 201
    libro_id = resp.json()["Id"]

    response = client.delete(f"/libros/{libro_id}", headers=headers)
    assert response.status_code == 200

    response2 = client.get(f"/libros/{libro_id}", headers=headers)
    assert response2.status_code == 404

def test_20_usuario_normal_no_puede_crear_libro(user_token):
    """
    Verificar que usuario normal no puede crear libros (solo admin)

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/libros/
    - Headers:
        Authorization: Bearer {{user_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Cod_libro": 5006,
            "Nombre_libro": "Libro Prohibido"
        }
    - Expected: 403 Forbidden, message about Administrador
    """
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {"Cod_libro": 5006, "Nombre_libro": "Libro Prohibido"}
    response = client.post("/libros/", json=data, headers=headers)
    assert response.status_code == 403
    assert "Administrador" in response.json().get("detail", "")

# ==================== USERS & ROLES TESTS (TC-14, TC-17) ====================

def test_08_create_usuario_administrador(admin_token):
    """
    TC-14 | US-05 | Decisión | Crear usuario con rol Administrador (solo admin puede)

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/usuarios/
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Cod_usuario": 9998,
            "Correo": "nuevoadmin@test.com",
            "Contraseña": "Admin1234",
            "Persona": 1,
            "Rol": 1
        }
    - Expected: 201 Created, luego DELETE para limpiar
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "Cod_usuario": 9998,
        "Correo": "nuevoadmin@test.com",
        "Contraseña": "Admin1234",
        "Persona": 1,
        "Rol": 1
    }
    response = client.post("/usuarios/", json=data, headers=headers)
    assert response.status_code == 201
    usuario_id = response.json()["Id"]
    client.delete(f"/usuarios/{usuario_id}", headers=headers)

def test_16_editar_persona(admin_token):
    """
    Editar persona (CRUD)

    POSTMAN:
    - Method: PUT
    - URL: {{base_url}}/personas/{{persona_id}} (crear temporal primero)
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Nombre": "Persona Editada",
            "Telefono": "3007654321"
        }
    - Expected: 200 OK, nombre actualizado
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Cedula": "12345678", "Nombre": "Persona Test", "Telefono": "3001234567"}
    resp = client.post("/personas/", json=data, headers=headers)
    assert resp.status_code == 201
    persona_id = resp.json()["Id"]

    update_data = {"Nombre": "Persona Editada", "Telefono": "3007654321"}
    response = client.put(f"/personas/{persona_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["Nombre"] == "Persona Editada"

    client.delete(f"/personas/{persona_id}", headers=headers)

def test_17_eliminar_rol(admin_token):
    """
    Eliminar rol (solo admin)

    POSTMAN:
    - Method: DELETE
    - URL: {{base_url}}/roles/{{rol_id}} (crear temporal primero)
    - Headers: Authorization: Bearer {{admin_token}}
    - Body: None
    - Expected: 200 OK, luego GET 404
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Nombre": "RolPrueba"}
    resp = client.post("/roles/", json=data, headers=headers)
    assert resp.status_code == 201
    rol_id = resp.json()["Id"]

    response = client.delete(f"/roles/{rol_id}", headers=headers)
    assert response.status_code == 200

    response2 = client.get(f"/roles/{rol_id}", headers=headers)
    assert response2.status_code == 404

# ==================== LOANS TESTS (TC-04, TC-06, TC-11, TC-16, TC-18, TC-22, TC-23) ====================

def test_04_get_prestamos_sin_auth():
    """
    TC-06 | US-02 | Decisión | Intentar ver préstamos sin token

    POSTMAN:
    - Method: GET
    - URL: {{base_url}}/prestamos/
    - Headers: None (sin Authorization)
    - Body: None
    - Expected: 401 Unauthorized
    """
    response = client.get("/prestamos/")
    assert response.status_code == 401

def test_06_create_prestamo_sin_detalles(admin_token):
    """
    TC-11 | US-04 | Exhaustividad | Crear préstamo con lista vacía de detalles

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/prestamos/
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Usuario": 1,
            "detalles": []
        }
    - Expected: 422 Unprocessable Entity
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Usuario": 1, "detalles": []}
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 422

def test_10_devolver_prestamo_actualizar_detalle(admin_token):
    """
    TC-16 | US-04 | Decisión | Devolver préstamo actualizando detalle

    POSTMAN:
    - Method: PUT
    - URL: {{base_url}}/detalles-prestamo/{{detalle_id}} (crear préstamo primero)
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Fecha_devolucion_real": "2027-03-23"
        }
    - Expected: 200 OK
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    prestamo_data = {
        "Usuario": 4,
        "detalles": [{"Copia": 3, "Fecha_entrega_esperada": "2027-04-10"}]
    }
    resp = client.post("/prestamos/", json=prestamo_data, headers=headers)
    assert resp.status_code == 201
    detalle_id = resp.json()["detalles"][0]["Id"]

    data = {"Fecha_devolucion_real": "2027-03-23"}
    response = client.put(f"/detalles-prestamo/{detalle_id}", json=data, headers=headers)
    assert response.status_code == 200

    client.delete(f"/prestamos/{resp.json()['Id']}", headers=headers)

def test_14_flujo_completo_end_to_end(admin_token):
    """
    TC-20 | US-04 | Aceptación | Flujo completo: login → crear préstamo → verificar

    POSTMAN:
    - Crear copia: POST {{base_url}}/copias/
    - Crear préstamo: POST {{base_url}}/prestamos/ con la copia creada
    - Devolver copia: PUT {{base_url}}/detalles-prestamo/{{detalle_id}}
    - Eliminar préstamo: DELETE {{base_url}}/prestamos/{{prestamo_id}}
    - Expected: 201, 200, 200, luego 404
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Crear copia disponible para el flujo completo
    copy_data = {"Libro": 1, "Notas": "Copia prueba flujo completo", "Disponible": True}
    copy_resp = client.post("/copias/", json=copy_data, headers=headers)
    assert copy_resp.status_code == 201
    copy_id = copy_resp.json()["Id"]

    prestamo_data = {
        "Usuario": 4,
        "detalles": [{"Copia": copy_id, "Fecha_entrega_esperada": "2027-04-15"}]
    }
    resp = client.post("/prestamos/", json=prestamo_data, headers=headers)
    assert resp.status_code == 201
    prestamo_id = resp.json()["Id"]
    detalle_id = resp.json()["detalles"][0]["Id"]

    resp2 = client.get(f"/prestamos/{prestamo_id}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["Id"] == prestamo_id

    # Devolver el detalle antes de eliminar el préstamo
    devolucion_resp = client.put(
        f"/detalles-prestamo/{detalle_id}",
        json={"Fecha_devolucion_real": "2027-04-20"},
        headers=headers
    )
    assert devolucion_resp.status_code == 200

    resp3 = client.delete(f"/prestamos/{prestamo_id}", headers=headers)
    assert resp3.status_code == 200

    resp4 = client.get(f"/prestamos/{prestamo_id}", headers=headers)
    assert resp4.status_code == 404

    # Eliminar copia de prueba creada
    delete_copy_resp = client.delete(f"/copias/{copy_id}", headers=headers)
    assert delete_copy_resp.status_code == 200

def test_18_crear_prestamo_con_dos_copias(admin_token):
    """
    Crear préstamo con dos copias disponibles

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/prestamos/
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Usuario": 1,
            "detalles": [
                {"Copia": copy_id_1, "Fecha_entrega_esperada": "2027-04-01"},
                {"Copia": copy_id_2, "Fecha_entrega_esperada": "2027-04-01"}
            ]
        }
    - Expected: 201 Created, 2 detalles
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Crear dos copias disponibles para validación
    copy1_resp = client.post(
        "/copias/", json={"Libro": 1, "Notas": "Prueba copia 1", "Disponible": True}, headers=headers
    )
    assert copy1_resp.status_code == 201
    copy_id_1 = copy1_resp.json()["Id"]

    copy2_resp = client.post(
        "/copias/", json={"Libro": 1, "Notas": "Prueba copia 2", "Disponible": True}, headers=headers
    )
    assert copy2_resp.status_code == 201
    copy_id_2 = copy2_resp.json()["Id"]

    data = {
        "Usuario": 1,
        "detalles": [
            {"Copia": copy_id_1, "Fecha_entrega_esperada": "2027-04-01"},
            {"Copia": copy_id_2, "Fecha_entrega_esperada": "2027-04-01"}
        ]
    }
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 201
    assert len(response.json()["detalles"]) == 2

    prestamo_id = response.json()["Id"]
    detalle_ids = [detalle["Id"] for detalle in response.json()["detalles"]]

    # Devolver detalles para poder eliminar el préstamo y limpiar datos
    for detalle_id in detalle_ids:
        devolucion_resp = client.put(
            f"/detalles-prestamo/{detalle_id}",
            json={"Fecha_devolucion_real": "2027-04-20"},
            headers=headers
        )
        assert devolucion_resp.status_code == 200

    delete_resp = client.delete(f"/prestamos/{prestamo_id}", headers=headers)
    assert delete_resp.status_code == 200

    # Eliminar copias temporales
    resp_copy_1 = client.delete(f"/copias/{copy_id_1}", headers=headers)
    assert resp_copy_1.status_code == 200
    resp_copy_2 = client.delete(f"/copias/{copy_id_2}", headers=headers)
    assert resp_copy_2.status_code == 200

def test_19_crear_prestamo_copia_no_disponible(admin_token):
    """
    Crear préstamo con copia no disponible (caso negativo)

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/prestamos/
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Usuario": 1,
            "detalles": [{"Copia": 6, "Fecha_entrega_esperada": "2027-04-01"}]
        }
    - Expected: 400 Bad Request, message "no está disponible"
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Usuario": 1, "detalles": [{"Copia": 6, "Fecha_entrega_esperada": "2027-04-01"}]}
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 400
    assert "no está disponible" in response.json()["detail"]

# ==================== CHILDREN & FILTER TESTS (TC-08, TC-09) ====================

def test_05_get_libros_usuario_normal(user_token):
    """
    TC-08 | US-03 | Lógica de negocio | Usuario normal ve todos los libros (sin filtro)

    POSTMAN:
    - Method: GET
    - URL: {{base_url}}/libros/
    - Headers: Authorization: Bearer {{user_token}}
    - Body: None
    - Expected: 200 OK, libros con Es_Infantil true y false
    """
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/libros/", headers=headers)
    assert response.status_code == 200
    libros = response.json()
    assert any(l["Es_Infantil"] is False for l in libros), "Debería haber libros no infantiles"
    assert any(l["Es_Infantil"] is True for l in libros), "Debería haber libros infantiles"

def test_11_filtro_infantil_nino(nino_token):
    """
    TC-17 | US-03 | Exhaustividad | Niño solo ve libros infantiles

    POSTMAN:
    - Method: GET
    - URL: {{base_url}}/libros/
    - Headers: Authorization: Bearer {{nino_token}}
    - Body: None
    - Expected: 200 OK, todos libros con Es_Infantil: true
    """
    headers = {"Authorization": f"Bearer {nino_token}"}
    response = client.get("/libros/", headers=headers)
    assert response.status_code == 200
    libros = response.json()
    for libro in libros:
        assert libro["Es_Infantil"] is True, f"Libro no infantil: {libro['Nombre_libro']}"

def test_09_create_copia_libro_inexistente(admin_token):
    """
    TC-15 | US-01 | Exhaustividad | Crear copia con libro inexistente

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/copias/
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Libro": 99999,
            "Notas": "Copia inválida",
            "Disponible": true
        }
    - Expected: 400 Bad Request, "Libro no existe"
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Libro": 99999, "Notas": "Copia inválida", "Disponible": True}
    response = client.post("/copias/", json=data, headers=headers)
    assert response.status_code == 400
    assert "Libro no existe" in response.json()["detail"]

# ==================== FASE 3 - DEFECTIVE CASES ====================

def test_fase3_01_registro_usuario_valido_con_datos_incompletos():
    """
    Fase 3 - Caso con defecto: Registro con campos requeridos incompletos

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/auth/register
    - Headers: Content-Type: application/json
    - Body (raw JSON):
        {
            "Cod_usuario": 9999,
            "Correo": "incompleto@test.com"
        }
    - Expected actual: 422 Unprocessable Entity
    - Observación: validación de campos obligatorios funcionando correctamente.
    """
    data = {
        "Cod_usuario": 9999,
        "Correo": "incompleto@test.com",
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 422  # Éxito: responde con validación correcta de campos obligatorios

def test_fase3_02_login_usuario_inexistente():
    """
    Fase 3 - Caso con defecto: Login con usuario inexistente

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/auth/login
    - Headers: Content-Type: application/x-www-form-urlencoded
    - Body (form-data):
        username: noexiste@library.com
        password: Cualquier123
    - Expected actual: 401 Unauthorized
    - Observación: comportamiento correcto. El sistema rechaza credenciales inválidas.
    """
    response = client.post(
        "/auth/login", 
        data={"username": "noexiste@library.com", "password": "Cualquier123"}
    )
    assert response.status_code == 401  # Éxito: usuario inexistente no puede iniciar sesión

def test_fase3_03_recuperacion_contrasena_correo_no_registrado():
    """
    Fase 3 - Caso con defecto: Recuperación de contraseña con correo inexistente

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/auth/recover
    - Headers: Content-Type: application/json
    - Body (raw JSON):
        {
            "email": "noexiste@library.com"
        }
    - Expected actual: 404 Not Found
    - Observación: el endpoint de recuperación no está implementado en la API.
    """
    response = client.post("/auth/recover", json={"email": "noexiste@library.com"})
    assert response.status_code == 404  # Éxito esperado: endpoint de recuperación ausente actualmente

def test_fase3_04_crear_prestamo_sin_usuario(admin_token):
    """
    Fase 3 - Caso con defecto: Crear préstamo sin especificar Usuario

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/prestamos/
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "detalles": [{"Copia": 1, "Fecha_entrega_esperada": "2027-05-01"}]
        }
    - Expected actual: 422 Unprocessable Entity
    - Observación: validación de estructura funcionando. Usuario es obligatorio para crear préstamo.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"detalles": [{"Copia": 1, "Fecha_entrega_esperada": "2027-05-01"}]}
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 422  # Éxito: rechaza préstamos sin Usuario

def test_fase3_05_actualizar_libro_sin_auth():
    """
    Fase 3 - Caso con defecto: Actualizar libro sin token de autenticación

    POSTMAN:
    - Method: PUT
    - URL: {{base_url}}/libros/1
    - Headers: Content-Type: application/json
    - Body (raw JSON):
        {
            "Nombre_libro": "Libro Modificado Sin Auth"
        }
    - Expected actual: 401 Unauthorized
    - Observación: comportamiento correcto. Actualización sin auth es rechazada.
    """
    data = {"Nombre_libro": "Libro Modificado Sin Auth"}
    response = client.put("/libros/1", json=data)
    assert response.status_code == 401  # Éxito: no permite modificación sin autenticación

# ==================== FASE 3 - SUCCESSFUL CASES ====================

def test_fase3_06_login_usuario_normal_ok():
    """
    Fase 3 - Caso exitoso: Login con usuario normal

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/auth/login
    - Headers: Content-Type: application/x-www-form-urlencoded
    - Body (form-data):
        username: carlos.lector@gmail.com
        password: Carlos789*
    - Expected: 200 OK, access_token válido
    - Observación: prueba exitosa de autenticación para usuario normal.
    """
    response = client.post(
        "/auth/login", 
        data={"username": "carlos.lector@gmail.com", "password": "Carlos789*"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()  # Éxito: token generado correctamente

def test_fase3_07_get_libros_con_paginacion_limit_3(admin_token):
    """
    Fase 3 - Caso exitoso: Listado paginado con limit pequeño

    POSTMAN:
    - Method: GET
    - URL: {{base_url}}/libros/?skip=0&limit=3
    - Headers: Authorization: Bearer {{admin_token}}
    - Body: None
    - Expected: 200 OK, <=3 libros
    - Observación: prueba exitosa para paginación de libros.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/libros/?skip=0&limit=3", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) <= 3  # Éxito: paginación funciona correctamente

def test_fase3_08_eliminar_persona_temporal(admin_token):
    """
    Fase 3 - Caso exitoso: Eliminar persona creada temporalmente

    POSTMAN:
    - Method: DELETE
    - URL: {{base_url}}/personas/{{persona_id}} (crear temporal)
    - Headers: Authorization: Bearer {{admin_token}}
    - Body: None
    - Expected: 200 OK
    - Observación: prueba exitosa de creación y eliminación de persona.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Cedula": "987654321", "Nombre": "Temporal Fase3", "Telefono": "3001112233"}
    resp = client.post("/personas/", json=data, headers=headers)
    persona_id = resp.json()["Id"]
    
    response = client.delete(f"/personas/{persona_id}", headers=headers)
    assert response.status_code == 200  # Éxito: persona temporal eliminada con éxito

# ==================== FASE 3 - IN PROGRESS CASES ====================

@pytest.mark.xfail(reason="En ejecución - pendiente implementación completa del endpoint")
def test_fase3_09_recuperacion_contrasena(admin_token):
    """
    Fase 3 - Caso en ejecución: Recuperación de contraseña

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/auth/recover
    - Headers: Content-Type: application/json
    - Body (raw JSON):
        {
            "email": "betty.admin@library.com"
        }
    - Expected: 200 OK si el endpoint estuviera completo
    - Observación: caso en ejecución. El endpoint está marcado como pendiente de implementación.
    """
    response = client.post("/auth/recover", json={"email": "betty.admin@library.com"})
    assert response.status_code == 200  # En ejecución: pendiente de completarse

def test_fase3_10_crear_prestamo_fecha_pasada(admin_token):
    """
    Fase 3 - Caso en ejecución: Crear préstamo con fecha de entrega en el pasado 

    POSTMAN:
    - Method: POST
    - URL: {{base_url}}/prestamos/
    - Headers:
        Authorization: Bearer {{admin_token}}
        Content-Type: application/json
    - Body (raw JSON):
        {
            "Usuario": 1,
            "detalles": [{"Copia": 1, "Fecha_entrega_esperada": "2025-01-01"}]
        }
    - Expected actual: 400 Bad Request
    - Observación: la validación de fecha pasada está funcionando correctamente.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "Usuario": 1,
        "detalles": [{"Copia": 1, "Fecha_entrega_esperada": "2025-01-01"}]
    }
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 400  # Éxito: rechaza mejoras con fecha de entrega pasada
    
