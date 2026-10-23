from datetime import date
from decimal import Decimal, InvalidOperation

import psycopg

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.excepciones import ErrorPersistencia


class EmpleadoRepositorio:
    def __init__(self, conexion):
        self.__conexion = conexion

    def crear(self, empleado: Empleado, departamento_id: int) -> Empleado:
        parametros = self._obtener_parametros(empleado, departamento_id)

        filas = self._ejecutar(
            """
            INSERT INTO ecotech.empleado (
                nombre, direccion, telefono, email,
                fecha_inicio_contrato, salario, departamento_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            parametros
        )

        return self.obtener_por_id(filas[0][0])

    def obtener_por_id(self, id_empleado: int):
        filas = self._ejecutar(
            """
            SELECT e.id, e.nombre, e.direccion, e.telefono, e.email,
                   e.fecha_inicio_contrato, e.salario,
                   d.id, d.nombre
            FROM ecotech.empleado AS e
            JOIN ecotech.departamento AS d ON d.id = e.departamento_id
            WHERE e.id = %s
            """,
            (id_empleado,)
        )

        if not filas:
            return None

        return self._fila_a_empleado(filas[0])

    def listar(self) -> list:
        filas = self._ejecutar(
            """
            SELECT e.id, e.nombre, e.direccion, e.telefono, e.email,
                   e.fecha_inicio_contrato, e.salario,
                   d.id, d.nombre
            FROM ecotech.empleado AS e
            JOIN ecotech.departamento AS d ON d.id = e.departamento_id
            ORDER BY e.id
            """
        )

        empleados = []
        for fila in filas:
            empleados.append(self._fila_a_empleado(fila))

        return empleados

    def actualizar(self, empleado: Empleado, departamento_id: int) -> Empleado:
        parametros = self._obtener_parametros(empleado, departamento_id)

        filas = self._ejecutar(
            """
            UPDATE ecotech.empleado
            SET nombre = %s,
                direccion = %s,
                telefono = %s,
                email = %s,
                fecha_inicio_contrato = %s,
                salario = %s,
                departamento_id = %s
            WHERE id = %s
            RETURNING id
            """,
            parametros + (empleado.get_id(),)
        )

        if not filas:
            raise ValueError("El empleado no existe")

        return self.obtener_por_id(filas[0][0])

    def eliminar(self, id_empleado: int) -> bool:
        filas = self._ejecutar(
            """
            DELETE FROM ecotech.empleado
            WHERE id = %s
            RETURNING id
            """,
            (id_empleado,)
        )

        return bool(filas)

    def _obtener_parametros(self, empleado, departamento_id):
        if not isinstance(empleado, Empleado):
            raise ValueError("Se debe entregar un objeto Empleado")

        textos = (
            empleado.get_nombre(),
            empleado.direccion,
            empleado.telefono,
            empleado.email
        )

        for texto in textos:
            if not isinstance(texto, str) or not texto.strip():
                raise ValueError("Los datos de contacto no pueden estar vacíos")

        if not isinstance(empleado.fecha_inicio_contrato, date):
            raise ValueError("La fecha del contrato debe ser un objeto date")

        if isinstance(departamento_id, bool) or not isinstance(departamento_id, int):
            raise ValueError("El ID del departamento debe ser un entero")

        if departamento_id <= 0:
            raise ValueError("El ID del departamento debe ser positivo")

        if isinstance(empleado.get_salario(), bool):
            raise ValueError("El salario debe ser un número válido")

        try:
            salario = Decimal(str(empleado.get_salario()))
        except (InvalidOperation, ValueError) as error:
            raise ValueError("El salario debe ser un número válido") from error

        if not salario.is_finite() or salario <= 0 or salario > Decimal("9999999999.99"):
            raise ValueError("El salario está fuera del rango permitido")

        if salario != salario.quantize(Decimal("0.01")):
            raise ValueError("El salario debe tener como máximo dos decimales")

        return (
            empleado.get_nombre().strip(),
            empleado.direccion.strip(),
            empleado.telefono.strip(),
            empleado.email.strip(),
            empleado.fecha_inicio_contrato,
            salario,
            departamento_id
        )

    def _ejecutar(self, consulta, parametros=()):
        try:
            with self.__conexion.cursor() as cursor:
                cursor.execute(consulta, parametros)
                return cursor.fetchall()

        except psycopg.errors.ForeignKeyViolation as error:
            raise ErrorPersistencia(
                "La operación contiene una relación inválida; "
                "comprueba que el departamento exista"
            ) from error

        except psycopg.errors.CheckViolation as error:
            raise ErrorPersistencia(
                "Los datos no cumplen las restricciones de la base de datos"
            ) from error

        except psycopg.Error as error:
            raise ErrorPersistencia(
                "Falló la operación de empleados en la base de datos"
            ) from error

    def _fila_a_empleado(self, fila) -> Empleado:
        empleado = Empleado(
            nombre=fila[1],
            direccion=fila[2],
            telefono=fila[3],
            email=fila[4],
            id_empleado=fila[0],
            fecha_inicio_contrato=fila[5],
            salario=fila[6]
        )

        departamento = Departamento(
            id_departamento=fila[7],
            nombre=fila[8]
        )
        departamento.asignar_empleado(empleado)

        return empleado
