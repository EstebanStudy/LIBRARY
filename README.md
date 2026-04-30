# 📚 LIBRARY – Sistema de Gestión de Biblioteca

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss)
![SQL Server](https://img.shields.io/badge/SQL_Server-2019-CC2927?logo=microsoft-sql-server)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Descripción

**LIBRARY** es un sistema completo de gestión bibliotecaria desarrollado con **FastAPI** (backend) y **HTML/CSS/JS** con **TailwindCSS** (frontend). Permite administrar el catálogo de libros, copias, usuarios, préstamos y devoluciones, con control de roles (Administrador, Usuario, Niños) y validaciones de negocio robustas.

El proyecto fue desarrollado como parte de la asignatura **Pruebas y Calidad del Software** en el Instituto Tecnológico Metropolitano (ITM), con el objetivo de aplicar técnicas de diseño de pruebas, cobertura y garantía de calidad.

---

## 🚀 Características

- **Autenticación JWT** con roles diferenciados.
- **CRUD completo** para libros, copias, personas, usuarios y roles.
- **Gestión de préstamos** con múltiples copias por préstamo.
- **Filtro automático de contenido infantil** para usuarios con rol "Niños".
- **Validaciones de unicidad** (código de libro, correo de usuario, etc.).
- **Interfaz responsive** y amigable con TailwindCSS.
- **Documentación automática** de la API con Swagger UI.

---

## 🛠️ Tecnologías utilizadas

| Capa | Tecnologías |
|------|-------------|
| **Backend** | FastAPI, SQLAlchemy, Pydantic, python-jose, passlib, python-dotenv |
| **Base de datos** | SQL Server (compatible con cualquier DB relacional via SQLAlchemy) |
| **Frontend** | HTML5, TailwindCSS, JavaScript (fetch API) |
| **Pruebas** | pytest, pytest-cov, httpx, TestClient de FastAPI |

---

## 📁 Estructura del proyecto
LIBRARY/
├── app/
│ ├── core/ # Configuración, seguridad, dependencias
│ ├── crud/ # Operaciones CRUD
│ ├── database/ # Conexión y sesión de BD
│ ├── models/ # Modelos SQLAlchemy
│ ├── routers/ # Endpoints de la API
│ └── schemas/ # Modelos Pydantic (validación)
├── frontend/ # Archivos estáticos HTML/CSS/JS
│ ├── js/
│ │ ├── app.js # Utilidades globales y mensajes
│ │ ├── auth.js # Lógica de login
│ │ └── protect.js # Autenticación de rutas frontend
│ ├── dashboard.html
│ ├── login.html
│ ├── libros.html
│ ├── prestamos.html
│ ├── copias.html
│ ├── personas.html
│ ├── roles.html
│ ├── usuario.html
│ └── detalles-prestamo.html
├── tests/ # Pruebas automatizadas (pytest)
├── main.py # Punto de entrada de la aplicación
├── requirements.txt # Dependencias del backend
├── migrate_to_script_inicial.sql # Script de migración con esquema y datos de prueba
├── .env # Variables de entorno (no incluido en repo)
└── README.md # Este archivo

## 🗄️ Esquema de Base de Datos

El esquema incluye las siguientes tablas principales:

- **Roles**: Gestión de roles (Administrador, Usuario, Niños).
- **Personas**: Información de personas con campos como Nombre, Correo, Teléfono, Dirección.
- **Usuarios**: Autenticación con hash de contraseña y sal UUID.
- **Libros**: Catálogo con Código, Título, Autor, Género, Es_Infantil.
- **Copias**: Instancias físicas de libros.
- **Préstamos**: Registros de préstamos con fecha de entrega.
- **Detalles_Préstamo**: Asociación de copias a préstamos con estado de devolución.

Para inicializar la base de datos, ejecuta el script `migrate_to_script_inicial.sql` que incluye el esquema completo y datos de prueba para desarrollo.

## 🔧 Instalación y configuración

1. Clonar el repositorio

git clone https://github.com/EstebanStudy/LIBRARY.git
cd LIBRARY

2. Configurar entorno virtual (recomendado)

python -m venv venv
# Activar en Windows
venv\Scripts\activate
# En Linux/Mac
source venv/bin/activate

3. Instalar dependencias
bash
pip install -r requirements.txt

4. Configurar variables de entorno
Crea un archivo .env en la raíz con el siguiente contenido:

DATABASE_URL=mssql+pyodbc://usuario:contraseña@servidor/biblioteca?driver=ODBC+Driver+17+for+SQL+Server
SECRET_KEY=tu-clave-secreta-muy-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

⚠️ Ajusta la cadena de conexión según tu motor de base de datos. El proyecto usa SQL Server, pero puedes adaptarlo a PostgreSQL, MySQL, etc. cambiando el driver.

5. Crear las tablas

Ejecuta el script SQL `migrate_to_script_inicial.sql` en tu base de datos para crear las tablas y poblar con datos de prueba. Alternativamente, puedes dejar que SQLAlchemy cree las tablas automáticamente al iniciar la aplicación (si `Base.metadata.create_all` está activo en `main.py`).

▶️ Ejecutar la aplicación

Backend
uvicorn main:app --reload

La API estará disponible en http://127.0.0.1:8000.
    Documentación interactiva: http://127.0.0.1:8000/docs
    Redoc: http://127.0.0.1:8000/redoc

Frontend
Los archivos estáticos están en la carpeta frontend/. Puedes servirlos con cualquier servidor HTTP simple, por ejemplo con Live Server de VS Code o con:

python -m http.server 5500 --directory frontend

Luego accede a http://localhost:5500/login.html.

📡 Endpoints principales

Método	Ruta	Descripción	Roles permitidos
POST	/auth/login	Inicio de sesión	Cualquiera
POST	/auth/register	Registro de usuario	Cualquiera
GET	/libros/	Listar libros (filtro infantil automático)	Autenticado
POST	/libros/	Crear libro	Administrador
PUT	/libros/{id}	Actualizar libro	Administrador
DELETE	/libros/{id}	Eliminar libro	Administrador
GET	/copias/	Listar copias	Autenticado
POST	/copias/	Crear copia	Administrador
GET	/prestamos/	Listar todos los préstamos	Autenticado
POST	/prestamos/	Crear préstamo	Autenticado
DELETE	/prestamos/{id}	Devolver préstamo (eliminar)	Administrador
GET	/personas/	Listar personas	Autenticado
PUT	/personas/{id}	Actualizar persona	Administrador
DELETE	/personas/{id}	Eliminar persona	Administrador
...	...	...	...
Consulta la documentación Swagger para una lista completa.

🧪 Pruebas automatizadas
El proyecto incluye una suite de pruebas con pytest. Para ejecutarlas:

pytest tests/ -v --tb=short

Para ver la cobertura:

pytest tests/ --cov=app --cov-report=html

Las pruebas cubren los casos descritos en el informe de calidad (TC-01 a TC-20) y validan la lógica de negocio, autorización, errores y flujos completos.

📝 Mejoras implementadas (última versión)

- **Compatibilidad con SQL Server**: Se agregó `{"implicit_returning": False}` a todos los modelos para evitar conflictos con triggers en INSERT/UPDATE.
- **Nuevos campos en modelos**:
  - `Direccion` agregado a la tabla `Persona` para almacenar direcciones.
  - `Es_Infantil` agregado a la tabla `Libro` para marcar libros infantiles.
- **Restricciones de integridad en CRUD**:
  - Prevención de eliminación de préstamos activos (con detalles no devueltos).
  - Prevención de eliminación de detalles de préstamo no devueltos.
- **Mejoras en el frontend**:
  - Estándarización de mensajes con helpers globales en `js/app.js` (`mostrarAlerta` y sobrescritura de `alert()` para estilos consistentes).
  - Inclusión de `js/app.js` en todos los archivos HTML para utilidades globales.
  - Agregado de botones de eliminación para préstamos completados en `prestamos.html`.
- **Script de migración**: `migrate_to_script_inicial.sql` incluye esquema completo y datos de prueba para desarrollo.
- **Mensajes profesionales**: Todos los mensajes de error y confirmación estandarizados para una mejor UX.

🤝 Contribuciones
Este proyecto fue desarrollado con fines académicos. Si deseas contribuir, por favor abre un issue o un pull request.

📄 Licencia
Distribuido bajo la licencia MIT. Consulta el archivo LICENSE para más información.

🧑‍💻 Autor
Esteban Quintero Yepes – GitHub

🙏 Agradecimientos
A mis compañeros 

¡Feliz lectura y préstamos! 📖✨