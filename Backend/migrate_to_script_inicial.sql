USE LIBRARY;
GO

-- =============================================
-- MIGRACIÓN A LA ESTRUCTURA DEL SCRIPT_INICIAL.SQL
-- =============================================

-- 1. Agregar columnas faltantes en Personas
IF COL_LENGTH('Personas', 'Direccion') IS NULL
BEGIN
    ALTER TABLE Personas
    ADD Direccion VARCHAR(255) NULL;
END
GO

-- 2. Agregar columnas de seguridad en Usuarios
IF COL_LENGTH('Usuarios', 'Salt') IS NULL
BEGIN
    ALTER TABLE Usuarios
    ADD Salt UNIQUEIDENTIFIER NULL;
END
GO

IF COL_LENGTH('Usuarios', 'PasswordHash') IS NULL
BEGIN
    ALTER TABLE Usuarios
    ADD PasswordHash VARBINARY(32) NULL;
END
GO

-- 3. Agregar columna Es_Infantil en Libros
IF COL_LENGTH('Libros', 'Es_Infantil') IS NULL
BEGIN
    ALTER TABLE Libros
    ADD Es_Infantil BIT NOT NULL CONSTRAINT DF_Libros_Es_Infantil DEFAULT(0);
END
GO

-- 4. Índices faltantes para mejorar rendimiento
IF NOT EXISTS (SELECT 1 FROM sys.indexes i JOIN sys.objects o ON i.object_id = o.object_id WHERE i.name = 'IX_Usuarios_Correo' AND o.name = 'Usuarios')
BEGIN
    CREATE NONCLUSTERED INDEX IX_Usuarios_Correo ON Usuarios (Correo);
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes i JOIN sys.objects o ON i.object_id = o.object_id WHERE i.name = 'IX_Usuarios_CodUsuario' AND o.name = 'Usuarios')
BEGIN
    CREATE NONCLUSTERED INDEX IX_Usuarios_CodUsuario ON Usuarios (Cod_usuario);
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes i JOIN sys.objects o ON i.object_id = o.object_id WHERE i.name = 'IX_Libros_CodLibro' AND o.name = 'Libros')
BEGIN
    CREATE NONCLUSTERED INDEX IX_Libros_CodLibro ON Libros (Cod_libro);
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes i JOIN sys.objects o ON i.object_id = o.object_id WHERE i.name = 'IX_Libros_Autor' AND o.name = 'Libros')
BEGIN
    CREATE NONCLUSTERED INDEX IX_Libros_Autor ON Libros (Autor);
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes i JOIN sys.objects o ON i.object_id = o.object_id WHERE i.name = 'IX_Prestamos_Usuario' AND o.name = 'Prestamos')
BEGIN
    CREATE NONCLUSTERED INDEX IX_Prestamos_Usuario ON Prestamos (Usuario);
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes i JOIN sys.objects o ON i.object_id = o.object_id WHERE i.name = 'IX_Prestamos_Fecha' AND o.name = 'Prestamos')
BEGIN
    CREATE NONCLUSTERED INDEX IX_Prestamos_Fecha ON Prestamos (Fecha_prestamo);
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes i JOIN sys.objects o ON i.object_id = o.object_id WHERE i.name = 'IX_Detalles_Prestamo' AND o.name = 'Detalles_Prestamo')
BEGIN
    CREATE NONCLUSTERED INDEX IX_Detalles_Prestamo ON Detalles_Prestamo (Prestamo);
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes i JOIN sys.objects o ON i.object_id = o.object_id WHERE i.name = 'IX_Detalles_Copia' AND o.name = 'Detalles_Prestamo')
BEGIN
    CREATE NONCLUSTERED INDEX IX_Detalles_Copia ON Detalles_Prestamo (Copia);
END
GO

-- 5. Procedimiento seguro de registro de usuario
CREATE OR ALTER PROCEDURE dbo.sp_RegistrarUsuario
    @Cod_usuario INT,
    @Correo NVARCHAR(255),
    @Password NVARCHAR(255),
    @PersonaId INT,
    @RolId INT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Salt UNIQUEIDENTIFIER = NEWID();
    DECLARE @Hash VARBINARY(32) = HASHBYTES('SHA2_256', @Password + CAST(@Salt AS NVARCHAR(36)));

    IF COL_LENGTH('Usuarios', 'Salt') IS NOT NULL AND COL_LENGTH('Usuarios', 'PasswordHash') IS NOT NULL
    BEGIN
        INSERT INTO Usuarios (Cod_usuario, Correo, Salt, PasswordHash, Persona, Rol)
        VALUES (@Cod_usuario, @Correo, @Salt, @Hash, @PersonaId, @RolId);
    END
    ELSE
    BEGIN
        RAISERROR('La tabla Usuarios no dispone del esquema de seguridad esperado.', 16, 1);
    END
END;
GO

-- 6. Función de verificación de contraseña
CREATE OR ALTER FUNCTION dbo.fn_VerificarPassword (
    @Correo NVARCHAR(255),
    @PasswordIngresada NVARCHAR(255)
)
RETURNS BIT
AS
BEGIN
    DECLARE @Result BIT = 0;
    DECLARE @Salt UNIQUEIDENTIFIER;
    DECLARE @HashAlmacenado VARBINARY(32);

    SELECT @Salt = Salt, @HashAlmacenado = PasswordHash
    FROM Usuarios
    WHERE Correo = @Correo;

    IF @Salt IS NOT NULL AND @HashAlmacenado IS NOT NULL
    BEGIN
        IF @HashAlmacenado = HASHBYTES('SHA2_256', @PasswordIngresada + CAST(@Salt AS NVARCHAR(36)))
            SET @Result = 1;
    END

    RETURN @Result;
END;
GO

-- 7. Triggers de auditoría
IF OBJECT_ID(N'trg_Audit_Roles', 'TR') IS NULL
BEGIN
    EXEC('CREATE TRIGGER trg_Audit_Roles ON Roles AFTER INSERT, UPDATE, DELETE AS BEGIN SET NOCOUNT ON; DECLARE @Accion NVARCHAR(50); IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted) SET @Accion = ''UPDATE''; ELSE IF EXISTS (SELECT * FROM inserted) SET @Accion = ''INSERT''; ELSE SET @Accion = ''DELETE''; INSERT INTO Auditorias (Entidad, Accion, Usuario_Responsable) VALUES (''Roles'', @Accion, SYSTEM_USER); END');
END
GO

IF OBJECT_ID(N'trg_Audit_Personas', 'TR') IS NULL
BEGIN
    EXEC('CREATE TRIGGER trg_Audit_Personas ON Personas AFTER INSERT, UPDATE, DELETE AS BEGIN SET NOCOUNT ON; DECLARE @Accion NVARCHAR(50); IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted) SET @Accion = ''UPDATE''; ELSE IF EXISTS (SELECT * FROM inserted) SET @Accion = ''INSERT''; ELSE SET @Accion = ''DELETE''; INSERT INTO Auditorias (Entidad, Accion, Usuario_Responsable) VALUES (''Personas'', @Accion, SYSTEM_USER); END');
END
GO

IF OBJECT_ID(N'trg_Audit_Usuarios', 'TR') IS NULL
BEGIN
    EXEC('CREATE TRIGGER trg_Audit_Usuarios ON Usuarios AFTER INSERT, UPDATE, DELETE AS BEGIN SET NOCOUNT ON; DECLARE @Accion NVARCHAR(50); IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted) SET @Accion = ''UPDATE''; ELSE IF EXISTS (SELECT * FROM inserted) SET @Accion = ''INSERT''; ELSE SET @Accion = ''DELETE''; INSERT INTO Auditorias (Entidad, Accion, Usuario_Responsable) VALUES (''Usuarios'', @Accion, SYSTEM_USER); END');
END
GO

IF OBJECT_ID(N'trg_Audit_Libros', 'TR') IS NULL
BEGIN
    EXEC('CREATE TRIGGER trg_Audit_Libros ON Libros AFTER INSERT, UPDATE, DELETE AS BEGIN SET NOCOUNT ON; DECLARE @Accion NVARCHAR(50); IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted) SET @Accion = ''UPDATE''; ELSE IF EXISTS (SELECT * FROM inserted) SET @Accion = ''INSERT''; ELSE SET @Accion = ''DELETE''; INSERT INTO Auditorias (Entidad, Accion, Usuario_Responsable) VALUES (''Libros'', @Accion, SYSTEM_USER); END');
END
GO

IF OBJECT_ID(N'trg_Audit_Copias', 'TR') IS NULL
BEGIN
    EXEC('CREATE TRIGGER trg_Audit_Copias ON Copias AFTER INSERT, UPDATE, DELETE AS BEGIN SET NOCOUNT ON; DECLARE @Accion NVARCHAR(50); IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted) SET @Accion = ''UPDATE''; ELSE IF EXISTS (SELECT * FROM inserted) SET @Accion = ''INSERT''; ELSE SET @Accion = ''DELETE''; INSERT INTO Auditorias (Entidad, Accion, Usuario_Responsable) VALUES (''Copias'', @Accion, SYSTEM_USER); END');
END
GO

IF OBJECT_ID(N'trg_Audit_Prestamos', 'TR') IS NULL
BEGIN
    EXEC('CREATE TRIGGER trg_Audit_Prestamos ON Prestamos AFTER INSERT, UPDATE, DELETE AS BEGIN SET NOCOUNT ON; DECLARE @Accion NVARCHAR(50); IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted) SET @Accion = ''UPDATE''; ELSE IF EXISTS (SELECT * FROM inserted) SET @Accion = ''INSERT''; ELSE SET @Accion = ''DELETE''; INSERT INTO Auditorias (Entidad, Accion, Usuario_Responsable) VALUES (''Prestamos'', @Accion, SYSTEM_USER); END');
END
GO

IF OBJECT_ID(N'trg_Audit_DetallesPrestamo', 'TR') IS NULL
BEGIN
    EXEC('CREATE TRIGGER trg_Audit_DetallesPrestamo ON Detalles_Prestamo AFTER INSERT, UPDATE, DELETE AS BEGIN SET NOCOUNT ON; DECLARE @Accion NVARCHAR(50); IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted) SET @Accion = ''UPDATE''; ELSE IF EXISTS (SELECT * FROM inserted) SET @Accion = ''INSERT''; ELSE SET @Accion = ''DELETE''; INSERT INTO Auditorias (Entidad, Accion, Usuario_Responsable) VALUES (''Detalles_Prestamo'', @Accion, SYSTEM_USER); END');
END
GO

PRINT 'Migración completada. Revise las columnas Salt/PasswordHash y los datos de acceso existentes.';
