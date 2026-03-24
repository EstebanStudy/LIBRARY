import pytest
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

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

# ==================== 20 CASOS DE PRUEBA (TC-01 a TC-20) ====================

def test_01_login_admin_ok():
    """TC-01 | US-05 | Equivalencia (válido) | Login correcto de administrador"""
    response = client.post("/auth/login", data={"username": "betty.admin@library.com", "password": "Admin2024!"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["role"] == "Administrador"

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

def test_04_get_prestamos_sin_auth():
    """TC-06 | US-02 | Decisión | Intentar ver préstamos sin token"""
    response = client.get("/prestamos/")
    assert response.status_code == 401

def test_05_get_libros_usuario_normal(user_token):
    """TC-08 | US-03 | Lógica de negocio | Usuario normal ve todos los libros (sin filtro)"""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/libros/", headers=headers)
    assert response.status_code == 200
    # Asegurar que hay libros infantiles y no infantiles (rol Usuario no filtra)
    libros = response.json()
    assert any(l["Es_Infantil"] is False for l in libros), "Debería haber libros no infantiles"
    assert any(l["Es_Infantil"] is True for l in libros), "Debería haber libros infantiles"

def test_06_create_prestamo_sin_detalles(admin_token):
    """TC-11 | US-04 | Exhaustividad | Crear préstamo con lista vacía de detalles"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Usuario": 1, "detalles": []}
    response = client.post("/prestamos/", json=data, headers=headers)
    assert response.status_code == 422  # Unprocessable Entity

def test_07_login_credenciales_incorrectas():
    """TC-13 | US-05 | Equivalencia (inválido) | Login con contraseña errónea"""
    response = client.post("/auth/login", data={"username": "betty.admin@library.com", "password": "mala"})
    assert response.status_code == 401

def test_08_create_usuario_administrador(admin_token):
    """TC-14 | US-05 | Decisión | Crear usuario con rol Administrador (solo admin puede)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "Cod_usuario": 9998,
        "Correo": "nuevoadmin@test.com",
        "Contraseña": "Admin1234",
        "Persona": 1,
        "Rol": 1  # Administrador
    }
    response = client.post("/usuarios/", json=data, headers=headers)
    assert response.status_code == 201
    # Limpiar después (opcional, pero podemos eliminar)
    usuario_id = response.json()["Id"]
    client.delete(f"/usuarios/{usuario_id}", headers=headers)

def test_09_create_copia_libro_inexistente(admin_token):
    """TC-15 | US-01 | Exhaustividad | Crear copia con libro inexistente"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"Libro": 99999, "Notas": "Copia inválida", "Disponible": True}
    response = client.post("/copias/", json=data, headers=headers)
    assert response.status_code == 400
    assert "Libro no existe" in response.json()["detail"]

def test_10_devolver_prestamo_actualizar_detalle(admin_token):
    """TC-16 | US-04 | Decisión | Devolver préstamo actualizando detalle"""
    # Primero crear un préstamo de prueba
    headers = {"Authorization": f"Bearer {admin_token}"}
    prestamo_data = {
        "Usuario": 4,
        "detalles": [{"Copia": 3, "Fecha_entrega_esperada": "2027-04-10"}]
    }
    resp = client.post("/prestamos/", json=prestamo_data, headers=headers)
    assert resp.status_code == 201
    detalle_id = resp.json()["detalles"][0]["Id"]

    # Actualizar fecha de devolución real
    data = {"Fecha_devolucion_real": "2027-03-23"}
    response = client.put(f"/detalles-prestamo/{detalle_id}", json=data, headers=headers)
    assert response.status_code == 200
    # Verificar que la copia ahora está disponible (opcional, se puede consultar)
    # Limpiar: eliminar préstamo
    client.delete(f"/prestamos/{resp.json()['Id']}", headers=headers)

def test_11_filtro_infantil_nino(nino_token):
    """TC-17 | US-03 | Exhaustividad | Niño solo ve libros infantiles"""
    headers = {"Authorization": f"Bearer {nino_token}"}
    response = client.get("/libros/", headers=headers)
    assert response.status_code == 200
    libros = response.json()
    for libro in libros:
        assert libro["Es_Infantil"] is True, f"Libro no infantil: {libro['Nombre_libro']}"

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

def test_13_update_libro_codigo_duplicado(admin_token):
    """TC-19 | US-01 | Decisión | Actualizar libro con código ya existente"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Crear un libro temporal
    data = {"Cod_libro": 7777, "Nombre_libro": "Temporal", "Autor": "Test"}
    resp = client.post("/libros/", json=data, headers=headers)
    assert resp.status_code == 201
    libro_id = resp.json()["Id"]

    # Intentar actualizar con código duplicado (5001 ya existe)
    update_data = {"Cod_libro": 5001, "Nombre_libro": "Actualizado"}
    response = client.put(f"/libros/{libro_id}", json=update_data, headers=headers)
    assert response.status_code == 400
    assert "código" in response.json()["detail"].lower() or "existe" in response.json()["detail"].lower()

    # Limpiar
    client.delete(f"/libros/{libro_id}", headers=headers)

def test_14_flujo_completo_end_to_end(admin_token):
    """TC-20 | US-04 | Aceptación | Flujo completo: login → crear préstamo → verificar"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # 1. Crear préstamo
    prestamo_data = {
        "Usuario": 4,
        "detalles": [{"Copia": 4, "Fecha_entrega_esperada": "2027-04-15"}]
    }
    resp = client.post("/prestamos/", json=prestamo_data, headers=headers)
    assert resp.status_code == 201
    prestamo_id = resp.json()["Id"]

    # 2. Verificar que el préstamo existe
    resp2 = client.get(f"/prestamos/{prestamo_id}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["Id"] == prestamo_id

    # 3. Devolver préstamo
    resp3 = client.delete(f"/prestamos/{prestamo_id}", headers=headers)
    assert resp3.status_code == 200

    # 4. Verificar que ya no existe
    resp4 = client.get(f"/prestamos/{prestamo_id}", headers=headers)
    assert resp4.status_code == 404

def test_15_eliminar_libro_existente(admin_token):
    """Caso extra: Eliminar libro correctamente"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Crear libro temporal
    data = {"Cod_libro": 8888, "Nombre_libro": "ParaEliminar", "Autor": "Test"}
    resp = client.post("/libros/", json=data, headers=headers)
    assert resp.status_code == 201
    libro_id = resp.json()["Id"]

    # Eliminar
    response = client.delete(f"/libros/{libro_id}", headers=headers)
    assert response.status_code == 200

    # Verificar que ya no existe
    response2 = client.get(f"/libros/{libro_id}", headers=headers)
    assert response2.status_code == 404

def test_16_editar_persona(admin_token):
    """Editar persona (CRUD)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Crear persona temporal
    data = {"Cedula": "12345678", "Nombre": "Persona Test", "Telefono": "3001234567"}
    resp = client.post("/personas/", json=data, headers=headers)
    assert resp.status_code == 201
    persona_id = resp.json()["Id"]

    # Editar
    update_data = {"Nombre": "Persona Editada", "Telefono": "3007654321"}
    response = client.put(f"/personas/{persona_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["Nombre"] == "Persona Editada"

    # Eliminar
    client.delete(f"/personas/{persona_id}", headers=headers)

def test_17_eliminar_rol(admin_token):
    """Eliminar rol (solo admin)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Crear rol temporal
    data = {"Nombre": "RolPrueba"}
    resp = client.post("/roles/", json=data, headers=headers)
    assert resp.status_code == 201
    rol_id = resp.json()["Id"]

    # Eliminar
    response = client.delete(f"/roles/{rol_id}", headers=headers)
    assert response.status_code == 200

    # Verificar que ya no existe
    response2 = client.get(f"/roles/{rol_id}", headers=headers)
    assert response2.status_code == 404

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

def test_20_usuario_normal_no_puede_crear_libro(user_token):
    """Verificar que usuario normal no puede crear libros (solo admin)"""
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {"Cod_libro": 5006, "Nombre_libro": "Libro Prohibido"}
    response = client.post("/libros/", json=data, headers=headers)
    assert response.status_code == 403
    assert "Administrador" in response.json().get("detail", "")