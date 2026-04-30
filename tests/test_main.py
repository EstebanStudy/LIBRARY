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
    """TC-01 | US-05 | Equivalencia (válido) | Login correcto de administrador"""
    response = client.post("/auth/login", data={"username": "betty.admin@library.com", "password": "Admin2024!"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["role"] == "Administrador"

def test_07_login_credenciales_incorrectas():
    """TC-13 | US-05 | Equivalencia (inválido) | Login con contraseña errónea"""
    response = client.post("/auth/login", data={"username": "betty.admin@library.com", "password": "mala"})
    assert response.status_code == 401

def test_12_register_correo_duplicado():
    """TC-18 | US-05 | Equivalencia (inválido) | Registrar con correo ya usado"""
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
    """TC-02 | US-01 | Equivalencia (inválido) | Crear libro con código duplicado"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Cod_libro": 5001, "Nombre_libro": "Libro Duplicado", "Autor": "Test"}
    response = client.post("/libros/", json=data, headers=headers)
    assert response.status_code == 400
    assert "código" in response.json()["detail"].lower() or "existe" in response.json()["detail"].lower()

def test_03_get_libros_paginados(admin_token):
    """TC-03 | US-01 | Exhaustividad | Leer libros con paginación (skip=0, limit=5)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/libros/?skip=0&limit=5", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) <= 5

def test_13_update_libro_codigo_duplicado(admin_token):
    """TC-19 | US-01 | Decisión | Actualizar libro con código ya existente"""
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
    """Caso extra: Eliminar libro correctamente"""
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
    """Verificar que usuario normal no puede crear libros (solo admin)"""
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {"Cod_libro": 5006, "Nombre_libro": "Libro Prohibido"}
    response = client.post("/libros/", json=data, headers=headers)
    assert response.status_code == 403
    assert "Administrador" in response.json().get("detail", "")

# ==================== USERS & ROLES TESTS (TC-14, TC-17) ====================

def test_08_create_usuario_administrador(admin_token):
    """TC-14 | US-05 | Decisión | Crear usuario con rol Administrador (solo admin puede)"""
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
    """Editar persona (CRUD)"""
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
    """Eliminar rol (solo admin)"""
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
    """TC-06 | US-02 | Decisión | Intentar ver préstamos sin token"""
    response = client.get("/prestamos/")
    assert response.status_code == 401

def test_06_create_prestamo_sin_detalles(admin_token):
    """TC-11 | US-04 | Exhaustividad | Crear préstamo con lista vacía de detalles"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Usuario": 1, "detalles": []}
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 422

def test_10_devolver_prestamo_actualizar_detalle(admin_token):
    """TC-16 | US-04 | Decisión | Devolver préstamo actualizando detalle"""
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
    """TC-20 | US-04 | Aceptación | Flujo completo: login → crear préstamo → verificar"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    prestamo_data = {
        "Usuario": 4,
        "detalles": [{"Copia": 4, "Fecha_entrega_esperada": "2027-04-15"}]
    }
    resp = client.post("/prestamos/", json=prestamo_data, headers=headers)
    assert resp.status_code == 201
    prestamo_id = resp.json()["Id"]

    resp2 = client.get(f"/prestamos/{prestamo_id}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["Id"] == prestamo_id

    resp3 = client.delete(f"/prestamos/{prestamo_id}", headers=headers)
    assert resp3.status_code == 200

    resp4 = client.get(f"/prestamos/{prestamo_id}", headers=headers)
    assert resp4.status_code == 404

def test_18_crear_prestamo_con_dos_copias(admin_token):
    """Crear préstamo con dos copias disponibles"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "Usuario": 1,
        "detalles": [
            {"Copia": 1, "Fecha_entrega_esperada": "2027-04-01"},
            {"Copia": 2, "Fecha_entrega_esperada": "2027-04-01"}
        ]
    }
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 201
    assert len(response.json()["detalles"]) == 2

def test_19_crear_prestamo_copia_no_disponible(admin_token):
    """Crear préstamo con copia no disponible (caso negativo)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Usuario": 1, "detalles": [{"Copia": 6, "Fecha_entrega_esperada": "2027-04-01"}]}
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 400
    assert "no está disponible" in response.json()["detail"]

# ==================== CHILDREN & FILTER TESTS (TC-08, TC-09) ====================

def test_05_get_libros_usuario_normal(user_token):
    """TC-08 | US-03 | Lógica de negocio | Usuario normal ve todos los libros (sin filtro)"""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/libros/", headers=headers)
    assert response.status_code == 200
    libros = response.json()
    assert any(l["Es_Infantil"] is False for l in libros), "Debería haber libros no infantiles"
    assert any(l["Es_Infantil"] is True for l in libros), "Debería haber libros infantiles"

def test_11_filtro_infantil_nino(nino_token):
    """TC-17 | US-03 | Exhaustividad | Niño solo ve libros infantiles"""
    headers = {"Authorization": f"Bearer {nino_token}"}
    response = client.get("/libros/", headers=headers)
    assert response.status_code == 200
    libros = response.json()
    for libro in libros:
        assert libro["Es_Infantil"] is True, f"Libro no infantil: {libro['Nombre_libro']}"

def test_09_create_copia_libro_inexistente(admin_token):
    """TC-15 | US-01 | Exhaustividad | Crear copia con libro inexistente"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Libro": 99999, "Notas": "Copia inválida", "Disponible": True}
    response = client.post("/copias/", json=data, headers=headers)
    assert response.status_code == 400
    assert "Libro no existe" in response.json()["detail"]

# ==================== FASE 3 - DEFECTIVE CASES ====================

def test_fase3_01_registro_usuario_valido_con_datos_incompletos():
    """Fase 3 - Caso con defecto: Registro con campos requeridos incompletos"""
    data = {
        "Cod_usuario": 9999,
        "Correo": "incompleto@test.com",
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 422

def test_fase3_02_login_usuario_inexistente():
    """Fase 3 - Caso con defecto: Login con usuario que no existe"""
    response = client.post(
        "/auth/login", 
        data={"username": "noexiste@library.com", "password": "Cualquier123"}
    )
    assert response.status_code == 404

def test_fase3_03_recuperacion_contrasena_correo_no_registrado():
    """Fase 3 - Caso con defecto: Recuperación de contraseña con correo inexistente"""
    response = client.post("/auth/recover", json={"email": "noexiste@library.com"})
    assert response.status_code == 200

def test_fase3_04_crear_prestamo_sin_usuario(admin_token):
    """Fase 3 - Caso con defecto: Crear préstamo sin especificar Usuario"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"detalles": [{"Copia": 1, "Fecha_entrega_esperada": "2027-05-01"}]}
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 422

def test_fase3_05_actualizar_libro_sin_auth():
    """Fase 3 - Caso con defecto: Actualizar libro sin token de autenticación"""
    data = {"Nombre_libro": "Libro Modificado Sin Auth"}
    response = client.put("/libros/1", json=data)
    assert response.status_code == 401

# ==================== FASE 3 - SUCCESSFUL CASES ====================

def test_fase3_06_login_usuario_normal_ok():
    """Fase 3 - Caso exitoso: Login con usuario normal"""
    response = client.post(
        "/auth/login", 
        data={"username": "carlos.lector@gmail.com", "password": "Carlos789*"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_fase3_07_get_libros_con_paginacion_limit_3(admin_token):
    """Fase 3 - Caso exitoso: Listado paginado con limit pequeño"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/libros/?skip=0&limit=3", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) <= 3

def test_fase3_08_eliminar_persona_temporal(admin_token):
    """Fase 3 - Caso exitoso: Eliminar persona creada temporalmente"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Cedula": "987654321", "Nombre": "Temporal Fase3", "Telefono": "3001112233"}
    resp = client.post("/personas/", json=data, headers=headers)
    persona_id = resp.json()["Id"]
    
    response = client.delete(f"/personas/{persona_id}", headers=headers)
    assert response.status_code == 200

# ==================== FASE 3 - IN PROGRESS CASES ====================

@pytest.mark.xfail(reason="En ejecución - pendiente implementación completa del endpoint")
def test_fase3_09_recuperacion_contrasena(admin_token):
    """Fase 3 - Caso en ejecución: Recuperación de contraseña"""
    response = client.post("/auth/recover", json={"email": "betty.admin@library.com"})
    assert response.status_code == 200

@pytest.mark.xfail(reason="En ejecución - validación de negocio pendiente")
def test_fase3_10_crear_prestamo_fecha_pasada(admin_token):
    """Fase 3 - Caso en ejecución: Crear préstamo con fecha de entrega en el pasado"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "Usuario": 1,
        "detalles": [{"Copia": 1, "Fecha_entrega_esperada": "2025-01-01"}]
    }
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 400
    
