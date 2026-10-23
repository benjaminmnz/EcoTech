import psycopg

from dominio.departamento import Departamento
from dominio.excepciones import ErrorPersistencia


class DepartamentoRepositorio:
    def __init__(self, conexion):
        self.__conexion = conexion

    def crear(self, nombre: str) -> Departamento:
        nombre = self._validar_nombre(nombre)

        filas = self._ejecutar(
            """
            INSERT INTO ecotech.departamento (nombre)
            VALUES (%s)
            RETURNING id, nombre
            """,
            (nombre,)
        )

        return self._fila_a_departamento(filas[0])

    def obtener_por_id(self, id_departamento: int):
        filas = self._ejecutar(
            """
            SELECT id, nombre
            FROM ecotech.departamento
            WHERE id = %s
            """,
            (id_departamento,)
        )

        if not filas:
            return None

        return self._fila_a_departamento(filas[0])

    def listar(self) -> list:
        filas = self._ejecutar(
            """
            SELECT id, nombre
            FROM ecotech.departamento
            ORDER BY id
            """
        )

        departamentos = []

        for fila in filas:
            departamentos.append(
                self._fila_a_departamento(fila)
            )

        return departamentos

    def actualizar(
        self,
        id_departamento: int,
        nuevo_nombre: str
    ) -> Departamento:
        nuevo_nombre = self._validar_nombre(nuevo_nombre)

        filas = self._ejecutar(
            """
            UPDATE ecotech.departamento
            SET nombre = %s
            WHERE id = %s
            RETURNING id, nombre
            """,
            (nuevo_nombre, id_departamento)
        )

        if not filas:
            raise ValueError("El departamento no existe")

        return self._fila_a_departamento(filas[0])

    def eliminar(self, id_departamento: int) -> bool:
        filas = self._ejecutar(
            """
            DELETE FROM ecotech.departamento
            WHERE id = %s
            RETURNING id
            """,
            (id_departamento,)
        )

        return bool(filas)

    def _validar_nombre(self, nombre: str) -> str:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError(
                "El nombre del departamento no puede estar vacío"
            )

        return nombre.strip()

    def _ejecutar(self, consulta, parametros=()):
        try:
            with self.__conexion.cursor() as cursor:
                cursor.execute(consulta, parametros)
                return cursor.fetchall()

        except psycopg.errors.ForeignKeyViolation as error:
            raise ErrorPersistencia(
                "La operación no puede completarse porque hay "
                "registros relacionados. Si intentas eliminar un "
                "departamento, primero reasigna sus empleados."
            ) from error

        except psycopg.Error as error:
            raise ErrorPersistencia(
                "Falló la operación de departamentos "
                "en la base de datos"
            ) from error

    def _fila_a_departamento(self, fila) -> Departamento:
        return Departamento(
            id_departamento=fila[0],
            nombre=fila[1]
        )

    def buscar_por_nombre(self, nombre: str) -> list:
        filas = self._ejecutar(
            """
            SELECT id, nombre
            FROM ecotech.departamento
            WHERE nombre = %s
            ORDER BY id
            """,
            (nombre,)
        )

        departamentos = []

        for fila in filas:
            departamentos.append(
                self._fila_a_departamento(fila)
            )

        return departamentos