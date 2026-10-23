from datetime import date
from decimal import Decimal

import psycopg

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from dominio.excepciones import ErrorPersistencia


class RegistroTiempoRepositorio:
    def __init__(self, conexion):
        self.__conexion = conexion

    def crear(self, empleado_id, proyecto_id, fecha, horas, descripcion):
        parametros = self._validar_datos(
            empleado_id, proyecto_id, fecha, horas, descripcion
        )
        filas = self._ejecutar(
            """
            INSERT INTO ecotech.registro_tiempo (
                fecha, horas_trabajadas, descripcion_tarea,
                empleado_id, proyecto_id
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            parametros
        )
        return self.obtener_por_id(filas[0][0])

    def obtener_por_id(self, registro_id):
        self._validar_id(registro_id)
        filas = self._consultar(registro_id=registro_id)
        if not filas:
            return None
        return self._fila_a_registro(filas[0])

    def listar(self):
        return self._convertir_filas(self._consultar())

    def listar_por_empleado(self, empleado_id):
        self._validar_id(empleado_id)
        return self._convertir_filas(self._consultar(empleado_id=empleado_id))

    def listar_por_proyecto(self, proyecto_id):
        self._validar_id(proyecto_id)
        return self._convertir_filas(self._consultar(proyecto_id=proyecto_id))

    def actualizar(self, registro_id, empleado_id, proyecto_id, fecha, horas, descripcion):
        self._validar_id(registro_id)
        parametros = self._validar_datos(
            empleado_id, proyecto_id, fecha, horas, descripcion
        )
        filas = self._ejecutar(
            """
            UPDATE ecotech.registro_tiempo
            SET fecha = %s, horas_trabajadas = %s, descripcion_tarea = %s,
                empleado_id = %s, proyecto_id = %s
            WHERE id = %s
            RETURNING id
            """,
            parametros + (registro_id,)
        )
        if not filas:
            raise ValueError("El registro no existe")
        return self.obtener_por_id(filas[0][0])

    def eliminar(self, registro_id):
        self._validar_id(registro_id)
        filas = self._ejecutar(
            """
            DELETE FROM ecotech.registro_tiempo
            WHERE id = %s
            RETURNING id
            """,
            (registro_id,)
        )
        return bool(filas)

    def _consultar(self, empleado_id=None, proyecto_id=None, registro_id=None):
        # Los filtros opcionales se pasan como datos, sin concatenar SQL.
        return self._ejecutar(
            """
            SELECT r.id, r.fecha, r.horas_trabajadas, r.descripcion_tarea,
                   e.id, e.nombre, e.direccion, e.telefono, e.email,
                   e.fecha_inicio_contrato, e.salario,
                   d.id, d.nombre,
                   p.id, p.nombre, p.descripcion, p.fecha_inicio
            FROM ecotech.registro_tiempo AS r
            JOIN ecotech.empleado AS e ON e.id = r.empleado_id
            JOIN ecotech.departamento AS d ON d.id = e.departamento_id
            JOIN ecotech.proyecto AS p ON p.id = r.proyecto_id
            WHERE (%s::bigint IS NULL OR r.empleado_id = %s)
              AND (%s::bigint IS NULL OR r.proyecto_id = %s)
              AND (%s::bigint IS NULL OR r.id = %s)
            ORDER BY r.fecha, r.id
            """,
            (empleado_id, empleado_id, proyecto_id, proyecto_id, registro_id, registro_id)
        )

    def _validar_id(self, identificador):
        if isinstance(identificador, bool) or not isinstance(identificador, int):
            raise ValueError("El identificador debe ser un entero")
        if identificador <= 0:
            raise ValueError("El identificador debe ser positivo")

    def _validar_datos(self, empleado_id, proyecto_id, fecha, horas, descripcion):
        self._validar_id(empleado_id)
        self._validar_id(proyecto_id)
        if not isinstance(fecha, date):
            raise ValueError("La fecha debe ser un objeto date")
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise ValueError("La descripción de la tarea no puede estar vacía")

        # Objeto temporal: reutiliza la validación de horas del dominio.
        # Su ID no se inserta: PostgreSQL genera el identificador real.
        temporal = RegistroTiempo(0, fecha, horas, descripcion)
        horas_decimal = Decimal(str(temporal.get_horas_trabajadas()))
        if horas_decimal != horas_decimal.quantize(Decimal("0.01")):
            raise ValueError("Las horas deben tener como máximo dos decimales")

        return fecha, horas_decimal, descripcion.strip(), empleado_id, proyecto_id

    def _ejecutar(self, consulta, parametros=()):
        try:
            with self.__conexion.cursor() as cursor:
                cursor.execute(consulta, parametros)
                return cursor.fetchall()
        except psycopg.errors.ForeignKeyViolation as error:
            raise ErrorPersistencia(
                "La operación contiene una relación inválida; el empleado "
                "debe existir y estar asignado al proyecto indicado"
            ) from error
        except psycopg.errors.CheckViolation as error:
            raise ErrorPersistencia(
                "Los datos no cumplen las restricciones del registro de tiempo"
            ) from error
        except psycopg.Error as error:
            raise ErrorPersistencia(
                "No se pudo completar la operación del registro de tiempo"
            ) from error

    def _convertir_filas(self, filas):
        registros = []
        for fila in filas:
            registros.append(self._fila_a_registro(fila))
        return registros

    def _fila_a_registro(self, fila):
        empleado = Empleado(
            nombre=fila[5], direccion=fila[6], telefono=fila[7], email=fila[8],
            id_empleado=fila[4], fecha_inicio_contrato=fila[9], salario=fila[10]
        )
        departamento = Departamento(fila[11], fila[12])
        departamento.asignar_empleado(empleado)

        proyecto = Proyecto(fila[13], fila[14], fila[15], fila[16])
        registro = RegistroTiempo(fila[0], fila[1], fila[2], fila[3])

        # Referencias del registro. No se cargan aquí todas las colecciones
        # de empleado/proyecto: esa reconstrucción se hará al integrar informes.
        registro.empleado = empleado
        registro.proyecto = proyecto
        return registro
