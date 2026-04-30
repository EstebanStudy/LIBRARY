USE master;
GO

-- =============================================
-- 1. REINICIO LIMPIO
-- =============================================
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'LIBRARY')
BEGIN
    ALTER DATABASE LIBRARY SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE LIBRARY;
END
GO

CREATE DATABASE LIBRARY;
GO

USE LIBRARY;
GO

-- =============================================
-- 2. TABLAS MAESTRAS
-- =============================================
CREATE TABLE [Roles](
    [Id] INT NOT NULL IDENTITY(1,1),
    [Nombre] NVARCHAR(50) NOT NULL,
    CONSTRAINT [PK_ROLES] PRIMARY KEY ([Id])
);

CREATE TABLE [Personas](
    [Id] INT NOT NULL IDENTITY(1,1),
    [Cedula] NVARCHAR(20) NOT NULL UNIQUE,
    [Nombre] NVARCHAR(100) NOT NULL,
    [Telefono] NVARCHAR(20),
    [Direccion] VARCHAR(255),
    CONSTRAINT [PK_PERSONAS] PRIMARY KEY ([Id])
);

-- =============================================
-- 3. USUARIOS (SEGURIDAD MEJORADA CON HASH + SALT)
-- =============================================
CREATE TABLE [Usuarios](
    [Id] INT NOT NULL IDENTITY(1,1),
    [Cod_usuario] INT NOT NULL UNIQUE,
    [Correo] NVARCHAR(255) NOT NULL UNIQUE,
    [Salt] UNIQUEIDENTIFIER NOT NULL,              -- ← Nuevo: salt aleatorio
    [PasswordHash] VARBINARY(32) NOT NULL,         -- ← Guarda hash SHA-256
    [Persona] INT NOT NULL,
    [Rol] INT NOT NULL,
    CONSTRAINT [PK_USUARIOS] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_Usuarios_Personas] FOREIGN KEY ([Persona]) REFERENCES [Personas] ([Id]) ON DELETE CASCADE,
    CONSTRAINT [FK_Usuarios_Rol] FOREIGN KEY ([Rol]) REFERENCES [Roles] ([Id])
);

-- =============================================
-- 4. CATÁLOGO DE LIBROS
-- =============================================
CREATE TABLE [Libros](
    [Id] INT NOT NULL IDENTITY(1,1),
    [Cod_libro] INT NOT NULL UNIQUE,
    [Nombre_libro] NVARCHAR(200) NOT NULL,
    [Fecha_publicacion] DATE,
    [Autor] NVARCHAR(100),
    [Portada_Url] NVARCHAR(MAX),
    [Es_Infantil] BIT NOT NULL DEFAULT 0,          -- ← Agregado aquí (evita ALTER posterior)
    CONSTRAINT [PK_LIBROS] PRIMARY KEY ([Id])
);

CREATE TABLE [Copias](
    [Id] INT NOT NULL IDENTITY (1, 1),
    [Libro] INT NOT NULL,
    [Notas] NVARCHAR(255),
    [Disponible] BIT DEFAULT 1,
    CONSTRAINT [PK_COPIAS] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_Copias_Libros] FOREIGN KEY ([Libro]) REFERENCES [Libros] ([Id]) ON DELETE CASCADE
);

-- =============================================
-- 5. PRÉSTAMOS
-- =============================================
CREATE TABLE [Prestamos](
    [Id] INT NOT NULL IDENTITY (1, 1),
    [Usuario] INT NOT NULL,
    [Fecha_prestamo] DATETIME DEFAULT GETDATE(),
    CONSTRAINT [PK_PRESTAMOS] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_Prestamos_Usuarios] FOREIGN KEY ([Usuario]) REFERENCES [Usuarios] ([Id])
);

CREATE TABLE [Detalles_Prestamo](
    [Id] INT NOT NULL IDENTITY (1, 1),
    [Prestamo] INT NOT NULL,
    [Copia] INT NOT NULL,
    [Fecha_entrega_esperada] DATE NOT NULL,
    [Fecha_devolucion_real] DATE NULL,
    CONSTRAINT [PK_DETALLES] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_Detalles_Prestamos] FOREIGN KEY ([Prestamo]) REFERENCES [Prestamos] ([Id]) ON DELETE CASCADE,
    CONSTRAINT [FK_Detalles_Copias] FOREIGN KEY ([Copia]) REFERENCES [Copias] ([Id])
);

-- =============================================
-- 6. AUDITORÍAS (automáticas vía triggers)
-- =============================================
CREATE TABLE [Auditorias](
    [Id] INT NOT NULL IDENTITY(1,1),
    [Entidad] NVARCHAR(50) NOT NULL,
    [Accion] NVARCHAR(50) NOT NULL,
    [Usuario_Responsable] NVARCHAR(100) NOT NULL,
    [Fecha] DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT [PK_Auditorias] PRIMARY KEY ([Id])
);
GO

-- =============================================
-- 7. ÍNDICES PARA RENDIMIENTO
-- =============================================
-- Índices sobre llaves foráneas y columnas de búsqueda frecuente
CREATE NONCLUSTERED INDEX [IX_Usuarios_Correo] ON [Usuarios] ([Correo]);
CREATE NONCLUSTERED INDEX [IX_Usuarios_CodUsuario] ON [Usuarios] ([Cod_usuario]);
CREATE NONCLUSTERED INDEX [IX_Libros_CodLibro] ON [Libros] ([Cod_libro]);
CREATE NONCLUSTERED INDEX [IX_Libros_Autor] ON [Libros] ([Autor]);
CREATE NONCLUSTERED INDEX [IX_Prestamos_Usuario] ON [Prestamos] ([Usuario]);
CREATE NONCLUSTERED INDEX [IX_Prestamos_Fecha] ON [Prestamos] ([Fecha_prestamo]);
CREATE NONCLUSTERED INDEX [IX_Detalles_Prestamo] ON [Detalles_Prestamo] ([Prestamo]);
CREATE NONCLUSTERED INDEX [IX_Detalles_Copia] ON [Detalles_Prestamo] ([Copia]);
GO

-- =============================================
-- 8. TRIGGERS DE AUDITORÍA AUTOMÁTICA
--    (registran INSERT, UPDATE, DELETE en tablas clave)
-- =============================================
-- Función auxiliar para obtener el usuario actual (puede ser SYSTEM_USER o un contexto)
CREATE FUNCTION dbo.GetCurrentAuditUser()
RETURNS NVARCHAR(100)
AS
BEGIN
    RETURN SYSTEM_USER;  -- También podría usar SUSER_SNAME() o un valor personalizado
END
GO

-- 8.1 Roles
CREATE TRIGGER [trg_Audit_Roles]
ON [Roles]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Accion NVARCHAR(50);
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        SET @Accion = 'UPDATE';
    ELSE IF EXISTS (SELECT * FROM inserted)
        SET @Accion = 'INSERT';
    ELSE
        SET @Accion = 'DELETE';

    INSERT INTO [Auditorias] ([Entidad], [Accion], [Usuario_Responsable])
    VALUES ('Roles', @Accion, dbo.GetCurrentAuditUser());
END
GO

-- 8.2 Personas
CREATE TRIGGER [trg_Audit_Personas]
ON [Personas]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Accion NVARCHAR(50);
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        SET @Accion = 'UPDATE';
    ELSE IF EXISTS (SELECT * FROM inserted)
        SET @Accion = 'INSERT';
    ELSE
        SET @Accion = 'DELETE';

    INSERT INTO [Auditorias] ([Entidad], [Accion], [Usuario_Responsable])
    VALUES ('Personas', @Accion, dbo.GetCurrentAuditUser());
END
GO

-- 8.3 Usuarios
CREATE TRIGGER [trg_Audit_Usuarios]
ON [Usuarios]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Accion NVARCHAR(50);
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        SET @Accion = 'UPDATE';
    ELSE IF EXISTS (SELECT * FROM inserted)
        SET @Accion = 'INSERT';
    ELSE
        SET @Accion = 'DELETE';

    INSERT INTO [Auditorias] ([Entidad], [Accion], [Usuario_Responsable])
    VALUES ('Usuarios', @Accion, dbo.GetCurrentAuditUser());
END
GO

-- 8.4 Libros
CREATE TRIGGER [trg_Audit_Libros]
ON [Libros]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Accion NVARCHAR(50);
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        SET @Accion = 'UPDATE';
    ELSE IF EXISTS (SELECT * FROM inserted)
        SET @Accion = 'INSERT';
    ELSE
        SET @Accion = 'DELETE';

    INSERT INTO [Auditorias] ([Entidad], [Accion], [Usuario_Responsable])
    VALUES ('Libros', @Accion, dbo.GetCurrentAuditUser());
END
GO

-- 8.5 Copias
CREATE TRIGGER [trg_Audit_Copias]
ON [Copias]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Accion NVARCHAR(50);
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        SET @Accion = 'UPDATE';
    ELSE IF EXISTS (SELECT * FROM inserted)
        SET @Accion = 'INSERT';
    ELSE
        SET @Accion = 'DELETE';

    INSERT INTO [Auditorias] ([Entidad], [Accion], [Usuario_Responsable])
    VALUES ('Copias', @Accion, dbo.GetCurrentAuditUser());
END
GO

-- 8.6 Prestamos
CREATE TRIGGER [trg_Audit_Prestamos]
ON [Prestamos]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Accion NVARCHAR(50);
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        SET @Accion = 'UPDATE';
    ELSE IF EXISTS (SELECT * FROM inserted)
        SET @Accion = 'INSERT';
    ELSE
        SET @Accion = 'DELETE';

    INSERT INTO [Auditorias] ([Entidad], [Accion], [Usuario_Responsable])
    VALUES ('Prestamos', @Accion, dbo.GetCurrentAuditUser());
END
GO

-- 8.7 Detalles_Prestamo
CREATE TRIGGER [trg_Audit_DetallesPrestamo]
ON [Detalles_Prestamo]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Accion NVARCHAR(50);
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        SET @Accion = 'UPDATE';
    ELSE IF EXISTS (SELECT * FROM inserted)
        SET @Accion = 'INSERT';
    ELSE
        SET @Accion = 'DELETE';

    INSERT INTO [Auditorias] ([Entidad], [Accion], [Usuario_Responsable])
    VALUES ('Detalles_Prestamo', @Accion, dbo.GetCurrentAuditUser());
END
GO

-- =============================================
-- 9. PROCEDIMIENTO ALMACENADO: REGISTRO SEGURO DE USUARIO
--    (genera salt, calcula hash)
-- =============================================
CREATE PROCEDURE [dbo].[sp_RegistrarUsuario]
    @Cod_usuario INT,
    @Correo NVARCHAR(255),
    @Password NVARCHAR(255),        -- Contraseña en texto plano (se recibe, no se almacena)
    @PersonaId INT,
    @RolId INT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Salt UNIQUEIDENTIFIER = NEWID();
    DECLARE @Hash VARBINARY(32) = HASHBYTES('SHA2_256', @Password + CAST(@Salt AS NVARCHAR(36)));

    INSERT INTO [Usuarios] ([Cod_usuario], [Correo], [Salt], [PasswordHash], [Persona], [Rol])
    VALUES (@Cod_usuario, @Correo, @Salt, @Hash, @PersonaId, @RolId);
END
GO

-- =============================================
-- 10. FUNCIÓN: VERIFICAR CONTRASEÑA
-- =============================================
CREATE FUNCTION [dbo].[fn_VerificarPassword] (
    @Correo NVARCHAR(255),
    @PasswordIngresada NVARCHAR(255)
)
RETURNS BIT
AS
BEGIN
    DECLARE @Result BIT = 0;
    DECLARE @Salt UNIQUEIDENTIFIER;
    DECLARE @HashAlmacenado VARBINARY(32);

    SELECT @Salt = [Salt], @HashAlmacenado = [PasswordHash]
    FROM [Usuarios]
    WHERE [Correo] = @Correo;

    IF @Salt IS NOT NULL AND @HashAlmacenado IS NOT NULL
    BEGIN
        IF @HashAlmacenado = HASHBYTES('SHA2_256', @PasswordIngresada + CAST(@Salt AS NVARCHAR(36)))
            SET @Result = 1;
    END

    RETURN @Result;
END
GO

-- =============================================
-- 11. VISTA: PRÉSTAMOS ACTIVOS
-- =============================================
CREATE VIEW [dbo].[vw_PrestamosActivos]
AS
SELECT 
    PR.Id AS PrestamoId,            -- ← Cambiado P por PR
    U.Cod_usuario AS CodigoUsuario,
    Pe.Nombre AS NombreUsuario,
    L.Nombre_libro AS Libro,
    C.Notas AS CopiaNotas,
    PR.Fecha_prestamo,
    DP.Fecha_entrega_esperada,
    DP.Fecha_devolucion_real,
    CASE WHEN DP.Fecha_devolucion_real IS NULL THEN 'Prestado' ELSE 'Devuelto' END AS Estado
FROM [Detalles_Prestamo] DP
INNER JOIN [Prestamos] PR ON DP.Prestamo = PR.Id
INNER JOIN [Copias] C ON DP.Copia = C.Id
INNER JOIN [Libros] L ON C.Libro = L.Id
INNER JOIN [Usuarios] U ON PR.Usuario = U.Id
INNER JOIN [Personas] Pe ON U.Persona = Pe.Id
WHERE DP.Fecha_devolucion_real IS NULL;
GO

-- =============================================
-- 12. INSERCIÓN DE DATOS DE PRUEBA
--     (con contraseñas hasheadas, triggers activos)
-- =============================================
INSERT INTO [Roles] ([Nombre]) VALUES 
(N'Administrador'), 
(N'Usuario'), 
(N'Niños');

INSERT INTO [Personas] ([Cedula], [Nombre], [Telefono]) VALUES
('102030', N'Beatriz Pinzón', '3001234567'),
('405060', N'Carlos Restrepo', '3109876543'),
('708090', N'Diana Turbay', '3152223344'),
('111222', N'Kevin Meza', '3205556677'),
('333444', N'Lucía Méndez', '3118889900'),
('555666', N'Samuel Eto', '34600112233'),
('777888', N'Mariana Pajón', '3014445566'),
('999000', N'Mateo García', '3187778899');

-- Registrar usuarios usando el procedimiento seguro
EXEC [dbo].[sp_RegistrarUsuario] 1001, 'betty.admin@library.com', 'Admin2024!', 1, 1;
EXEC [dbo].[sp_RegistrarUsuario] 2001, 'carlos.lector@gmail.com', 'Carlos789*', 2, 2;
EXEC [dbo].[sp_RegistrarUsuario] 2002, 'diana.investiga@outlook.com', 'D14n4_2024', 3, 2;
EXEC [dbo].[sp_RegistrarUsuario] 3001, 'kevin.kids@library.com', 'Cuentos123', 4, 3;
EXEC [dbo].[sp_RegistrarUsuario] 3002, 'lucia.escuela@correo.com', 'HadaMadrina', 5, 3;
EXEC [dbo].[sp_RegistrarUsuario] 2003, 'samuel.eto@inter.com', 'Goleador09', 6, 2;
EXEC [dbo].[sp_RegistrarUsuario] 1002, 'mariana.soporte@library.com', 'OroOlimpico', 7, 1;
EXEC [dbo].[sp_RegistrarUsuario] 3003, 'mateo.juega@correo.com', 'DinoRwar', 8, 3;

-- Libros
INSERT INTO [Libros] ([Cod_libro], [Nombre_libro], [Fecha_publicacion], [Autor], [Es_Infantil]) VALUES
(5001, N'El Principito', '1943-04-06', N'Antoine de Saint-Exupéry', 1),
(5002, N'Cálculo de Stewart', '2015-01-01', 'James Stewart', 0),
(5003, N'Donde viven los monstruos', '1963-10-09', 'Maurice Sendak', 1),
(5004, N'Harry Potter y la Piedra Filosofal', '1997-06-26', 'J.K. Rowling', 1),
(5005, N'Breve historia del tiempo', '1988-03-01', 'Stephen Hawking', 0);

-- Copias
INSERT INTO [Copias] ([Libro], [Notas], [Disponible]) VALUES
(1, N'Edición ilustrada', 1),
(2, 'Referencia sala 2', 1),
(3, 'Tapa dura - Infantil', 1),
(4, 'Saga completa vol 1', 1),
(5, N'Ciencia y Tecnología', 0);

-- Préstamos
INSERT INTO [Prestamos] ([Usuario], [Fecha_prestamo]) VALUES
(1, '2027-01-15 10:30:00'),
(4, '2027-02-01 14:20:00'),
(2, '2027-02-10 09:00:00'),
(5, '2027-02-15 16:45:00'),
(8, '2027-03-01 11:10:00'),
(3, GETDATE());

-- Detalles de préstamo
INSERT INTO [Detalles_Prestamo] 
([Prestamo], [Copia], [Fecha_entrega_esperada], [Fecha_devolucion_real]) 
VALUES
(1, 3, '2027-01-22', NULL),
(2, 4, '2027-02-08', NULL),
(3, 1, '2027-02-17', NULL),
(4, 5, '2027-02-22', NULL),
(5, 2, '2027-03-08', NULL),
(6, 4, '2027-03-20', NULL);

-- =============================================
-- 13. RESTRICCIONES CHECK (posteriores a los datos)
-- =============================================
-- Validar formato básico de correo
ALTER TABLE [Usuarios]
ADD CONSTRAINT CK_Usuarios_Correo CHECK ([Correo] LIKE '%_@__%.__%');

-- Fecha de publicación no futura
ALTER TABLE [Libros]
ADD CONSTRAINT CK_Libros_FechaPub CHECK ([Fecha_publicacion] <= GETDATE());

-- Longitud mínima de teléfono
ALTER TABLE [Personas]
ADD CONSTRAINT CK_Personas_Telefono CHECK (LEN([Telefono]) >= 7);

-- Fecha de entrega esperada: no más de 2 años en el pasado (para pruebas con datos 2027)
ALTER TABLE [Detalles_Prestamo]
ADD CONSTRAINT CK_Fechas_Entrega 
CHECK ([Fecha_entrega_esperada] >= DATEADD(YEAR, -2, CAST(GETDATE() AS DATE)));

-- =============================================
-- 14. CONSULTA DE VERIFICACIÓN
-- =============================================
SELECT N'Base de datos mejorada creada con éxito' AS Mensaje;

-- Mostrar algunos préstamos activos
SELECT * FROM [dbo].[vw_PrestamosActivos];

-- Probar verificación de contraseña (ejemplo)
SELECT dbo.fn_VerificarPassword('betty.admin@library.com', 'Admin2024!') AS BettyPasswordCorrecta;

-- Opcional: volver a master si se desea
USE master;