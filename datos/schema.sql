-- Agrupa las tablas de nuestro sistema.
CREATE SCHEMA IF NOT EXISTS ecotech;


-- Tabla de departamentos.
CREATE TABLE ecotech.departamento (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre TEXT NOT NULL CHECK (LENGTH(TRIM(nombre)) > 0)
);


-- Tabla de empleados.
CREATE TABLE ecotech.empleado (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre TEXT NOT NULL CHECK (LENGTH(TRIM(nombre)) > 0),
    direccion TEXT NOT NULL,
    telefono TEXT NOT NULL,
    email TEXT NOT NULL,
    fecha_inicio_contrato DATE NOT NULL,
    salario NUMERIC(12, 2) NOT NULL
        CHECK (salario > 0 AND salario <> 'NaN'::NUMERIC),
    departamento_id BIGINT NOT NULL,

    FOREIGN KEY (departamento_id)
        REFERENCES ecotech.departamento(id)
        ON DELETE RESTRICT
);

-- Tabla de proyectos.
CREATE TABLE ecotech.proyecto (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre TEXT NOT NULL CHECK (LENGTH(TRIM(nombre)) > 0),
    descripcion TEXT NOT NULL,
    fecha_inicio DATE NOT NULL
);

-- Asignaciones de empleados a proyectos.
CREATE TABLE ecotech.empleado_proyecto (
    empleado_id BIGINT NOT NULL,
    proyecto_id BIGINT NOT NULL,

    PRIMARY KEY (empleado_id, proyecto_id),

    FOREIGN KEY (empleado_id)
        REFERENCES ecotech.empleado(id)
        ON DELETE CASCADE,

    FOREIGN KEY (proyecto_id)
        REFERENCES ecotech.proyecto(id)
        ON DELETE CASCADE
);

-- Cuentas de acceso de los empleados.
CREATE TABLE ecotech.cuenta_usuario (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    usuario TEXT NOT NULL UNIQUE
        CHECK (LENGTH(TRIM(usuario)) > 0),

    contrasena_hash TEXT NOT NULL
        CHECK (LENGTH(TRIM(contrasena_hash)) > 0),

    rol_acceso TEXT NOT NULL
        CHECK (rol_acceso IN ('administrador', 'empleado')),

    empleado_id BIGINT NOT NULL UNIQUE,

    FOREIGN KEY (empleado_id)
        REFERENCES ecotech.empleado(id)
        ON DELETE CASCADE
);

-- Registros de tiempo trabajado.
CREATE TABLE ecotech.registro_tiempo (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    fecha DATE NOT NULL,

    horas_trabajadas NUMERIC(4, 2) NOT NULL
        CHECK (horas_trabajadas > 0 AND horas_trabajadas <= 24),

    descripcion_tarea TEXT NOT NULL
        CHECK (LENGTH(TRIM(descripcion_tarea)) > 0),

    empleado_id BIGINT NOT NULL,
    proyecto_id BIGINT NOT NULL,

    FOREIGN KEY (empleado_id)
        REFERENCES ecotech.empleado(id)
        ON DELETE CASCADE,

    FOREIGN KEY (proyecto_id)
        REFERENCES ecotech.proyecto(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (empleado_id, proyecto_id)
        REFERENCES ecotech.empleado_proyecto(empleado_id, proyecto_id)
        ON DELETE NO ACTION
        DEFERRABLE INITIALLY DEFERRED
);

-- Permite referenciar al empleado junto con su departamento.
ALTER TABLE ecotech.empleado
    ADD CONSTRAINT empleado_id_departamento_unico
    UNIQUE (id, departamento_id);


-- Agrega el gerente al departamento.
ALTER TABLE ecotech.departamento
    ADD COLUMN gerente_id BIGINT UNIQUE;


-- El gerente debe ser un empleado del mismo departamento.
ALTER TABLE ecotech.departamento
    ADD CONSTRAINT departamento_gerente_fk
    FOREIGN KEY (gerente_id, id)
    REFERENCES ecotech.empleado(id, departamento_id)
    ON DELETE SET NULL (gerente_id);

-- Activar seguridad por filas.
ALTER TABLE ecotech.departamento ENABLE ROW LEVEL SECURITY;
ALTER TABLE ecotech.empleado ENABLE ROW LEVEL SECURITY;
ALTER TABLE ecotech.proyecto ENABLE ROW LEVEL SECURITY;
ALTER TABLE ecotech.empleado_proyecto ENABLE ROW LEVEL SECURITY;
ALTER TABLE ecotech.cuenta_usuario ENABLE ROW LEVEL SECURITY;
ALTER TABLE ecotech.registro_tiempo ENABLE ROW LEVEL SECURITY;