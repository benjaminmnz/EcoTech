from datetime import date

import psycopg

from dominio.proyecto import Proyecto
from dominio.excepciones import ErrorPersistencia


class ProyectoRepositorio:
    def __init__(self, conexion):
        self.__conexion = conexion

    def crear(self, proyecto: Proyecto) -> Proyecto:
        parametros = self._obtener_parametros(proyecto)
        filas = self._ejecutar(
            """
            INSERT INTO ecotech.proyecto (nombre, descripcion, fecha_inicio)
            VALUES (%s, %s, %s)
            RETURNING id, nombre, descripcion, fecha_inicio
            """,
            parametros
        )
        return self._fila_a_proyecto(filas[0])

    def obtener_por_id(self, proyecto_id: int):
        filas = self._ejecutar(
            """
            SELECT id, nombre, descripcion, fecha_inicio
            FROM ecotech.proyecto
            WHERE id = %s
            """,
            (proyecto_id,)
        )
        if not filas:
            return None
        return self._fila_a_proyecto(filas[0])

    def listar(self) -> list:
        filas = self._ejecutar(
            """
            SELECT id, nombre, descripcion, fecha_inicio
            FROM ecotech.proyecto
            ORDER BY id
            """
        )
        proyectos = []
        for fila in filas:
            proyectos.append(self._fila_a_proyecto(fila))
        return proyectos

    def actualizar(self, proyecto: Proyecto) -> Proyecto:
        parametros = self._obtener_parametros(proyecto)
        filas = self._ejecutar(
            """
            UPDATE ecotech.proyecto
            SET nombre = %s, descripcion = %s, fecha_inicio = %s
            WHERE id = %s
            RETURNING id, nombre, descripcion, fecha_inicio
            """,
            parametros + (proyecto.get_id(),)
        )
        if not filas:
            raise ValueError("El proyecto no existe")
        return self._fila_a_proyecto(filas[0])

    def eliminar(self, proyecto_id: int) -> bool:
        filas = self._ejecutar(
            """
            DELETE FROM ecotech.proyecto
            WHERE id = %s
            RETURNING id
            """,
            (proyecto_id,)
        )
        return bool(filas)

    def asignar_empleado(self, proyecto_id: int, empleado_id: int):
        self._ejecutar(
            """
            INSERT INTO ecotech.empleado_proyecto (empleado_id, proyecto_id)
            VALUES (%s, %s)
            RETURNING empleado_id
            """,
            (empleado_id, proyecto_id)
        )

    def listar_ids_empleados(self, proyecto_id: int) -> list:
        filas = self._ejecutar(
            """
            SELECT empleado_id
            FROM ecotech.empleado_proyecto
            WHERE proyecto_id = %s
            ORDER BY empleado_id
            """,
            (proyecto_id,)
        )
        ids = []
        for fila in filas:
            ids.append(fila[0])
        return ids

    def quitar_empleado(self, proyecto_id: int, empleado_id: int) -> bool:
        filas = self._ejecutar(
            """
            DELETE FROM ecotech.empleado_proyecto
            WHERE empleado_id = %s AND proyecto_id = %s
            RETURNING empleado_id
            """,
            (empleado_id, proyecto_id)
        )
        return bool(filas)

    def _obtener_parametros(self, proyecto):
        if not isinstance(proyecto, Proyecto):
            raise ValueError("Se debe entregar un objeto Proyecto")
        if not isinstance(proyecto.nombre, str) or not proyecto.nombre.strip():
            raise ValueError("El nombre del proyecto no puede estar vacío")
        if not isinstance(proyecto.descripcion, str):
            raise ValueError("La descripción debe ser texto")
        if not isinstance(proyecto.fecha_inicio, date):
            raise ValueError("La fecha de inicio debe ser un objeto date")
        return proyecto.nombre.strip(), proyecto.descripcion, proyecto.fecha_inicio

    def _ejecutar(self, consulta, parametros=()):
        try:
            with self.__conexion.cursor() as cursor:
                cursor.execute(consulta, parametros)
                return cursor.fetchall()
        except psycopg.errors.UniqueViolation as error:
            raise ErrorPersistencia(
                "El empleado ya está asignado a este proyecto"
            ) from error
        except psycopg.errors.ForeignKeyViolation as error:
            raise ErrorPersistencia(
                "La operación contiene una relación inválida. Comprueba que "
                "empleado y proyecto existan y que no queden registros "
                "de tiempo dependiendo de la relación que intentas quitar."
            ) from error
        except psycopg.Error as error:
            raise ErrorPersistencia(
                "Falló la operación de proyectos en la base de datos"
            ) from error

    def _fila_a_proyecto(self, fila) -> Proyecto:
        # Reconstruye los datos básicos. Las relaciones se cargan por separado.
        return Proyecto(
            id_proyecto=fila[0],
            nombre=fila[1],
            descripcion=fila[2],
            fecha_inicio=fila[3]
        )

    def listar_asignaciones(self):
        return self._ejecutar(
            "SELECT proyecto_id, empleado_id FROM ecotech.empleado_proyecto ORDER BY proyecto_id, empleado_id"
        )

    def listar_por_empleado(self, empleado_id):
        filas = self._ejecutar(
            """
            SELECT p.id, p.nombre, p.descripcion, p.fecha_inicio
            FROM ecotech.proyecto AS p
            JOIN ecotech.empleado_proyecto AS ep ON ep.proyecto_id = p.id
            WHERE ep.empleado_id = %s
            ORDER BY p.id
            """,
            (empleado_id,)
        )
        return [self._fila_a_proyecto(fila) for fila in filas]
