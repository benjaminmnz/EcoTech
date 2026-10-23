import psycopg

from dominio.cuenta_usuario import CuentaUsuario
from dominio.excepciones import ErrorPersistencia


class CuentaUsuarioRepositorio:
    def __init__(self, conexion):
        self.__conexion = conexion

    def crear(self, cuenta: CuentaUsuario, empleado_id: int) -> CuentaUsuario:
        filas = self._ejecutar(
            """
            INSERT INTO ecotech.cuenta_usuario (
                usuario, contrasena_hash, rol_acceso, empleado_id
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id, usuario, contrasena_hash, rol_acceso
            """,
            (
                cuenta.usuario.strip(),
                cuenta.get_contrasena_hash(),
                cuenta.get_rol_acceso(),
                empleado_id
            )
        )

        return self._fila_a_cuenta(filas[0])

    def obtener_por_usuario(self, usuario: str):
        filas = self._ejecutar(
            """
            SELECT id, usuario, contrasena_hash, rol_acceso
            FROM ecotech.cuenta_usuario
            WHERE usuario = %s
            """,
            (usuario.strip(),)
        )

        if not filas:
            return None

        return self._fila_a_cuenta(filas[0])

    def obtener_por_empleado(self, empleado_id: int):
        filas = self._ejecutar(
            """
            SELECT id, usuario, contrasena_hash, rol_acceso
            FROM ecotech.cuenta_usuario
            WHERE empleado_id = %s
            """,
            (empleado_id,)
        )

        if not filas:
            return None

        return self._fila_a_cuenta(filas[0])

    def obtener_empleado_id(self, cuenta_id: int):
        filas = self._ejecutar(
            """
            SELECT empleado_id
            FROM ecotech.cuenta_usuario
            WHERE id = %s
            """,
            (cuenta_id,)
        )

        if not filas:
            return None

        return filas[0][0]

    def _ejecutar(self, consulta, parametros=()):
        try:
            with self.__conexion.cursor() as cursor:
                cursor.execute(consulta, parametros)
                return cursor.fetchall()

        except psycopg.errors.UniqueViolation as error:
            raise ErrorPersistencia(
                "El usuario ya existe o el empleado ya tiene una cuenta"
            ) from error

        except psycopg.errors.ForeignKeyViolation as error:
            raise ErrorPersistencia(
                "El empleado de la cuenta no existe"
            ) from error

        except psycopg.Error as error:
            raise ErrorPersistencia(
                "No se pudo completar la operación de la cuenta"
            ) from error

    def _fila_a_cuenta(self, fila) -> CuentaUsuario:
        return CuentaUsuario(
            id_cuenta=fila[0],
            usuario=fila[1],
            contrasena_hash=fila[2],
            rol_acceso=fila[3]
        )

    def listar_con_empleado(self):
        filas = self._ejecutar(
            """
            SELECT id, usuario, contrasena_hash, rol_acceso, empleado_id
            FROM ecotech.cuenta_usuario
            ORDER BY id
            """
        )
        return [(self._fila_a_cuenta(fila), fila[4]) for fila in filas]

    def actualizar_hash(self, cuenta_id, nuevo_hash):
        filas = self._ejecutar(
            """
            UPDATE ecotech.cuenta_usuario
            SET contrasena_hash = %s
            WHERE id = %s
            RETURNING id
            """,
            (nuevo_hash, cuenta_id)
        )
        if not filas:
            raise ValueError("La cuenta ya no existe")
