from datetime import date
from decimal import Decimal

from dominio.empleado import Empleado
from dominio.registro_tiempo import RegistroTiempo
from dominio.validaciones import identificador, texto, fecha_valida


class Proyecto:
    def __init__(self, id_proyecto: int, nombre: str, descripcion: str, fecha_inicio: date):
        self.__id = identificador(id_proyecto)
        self.nombre = texto(nombre, "El nombre del proyecto")
        self.descripcion = texto(descripcion, "La descripción")
        self.fecha_inicio = fecha_valida(fecha_inicio)
        self.__empleados = []
        self.__registros = []

    def get_id(self) -> int:
        return self.__id

    def asignar_empleado(self, empleado: Empleado):
        if not isinstance(empleado, Empleado):
            raise ValueError("Se debe entregar un empleado")
        if any(e.get_id() == empleado.get_id() for e in self.__empleados):
            raise ValueError("El empleado ya está asignado al proyecto")
        self.__empleados.append(empleado)

    def listar_empleados(self) -> list:
        return self.__empleados.copy()

    def listar_registros(self) -> list:
        return self.__registros.copy()

    def agregar_registro(self, registro: RegistroTiempo):
        if registro.proyecto is not None:
            raise ValueError("El registro ya tiene un proyecto")
        if registro.empleado is None:
            raise ValueError("El registro debe tener un empleado")
        if not any(e.get_id() == registro.empleado.get_id() for e in self.__empleados):
            raise ValueError("El empleado no está asignado al proyecto")
        if any(r.get_id() == registro.get_id() for r in self.__registros):
            raise ValueError("Ya existe el identificador del registro")
        self.__registros.append(registro)
        registro.proyecto = self

    def calcular_horas_totales(self) -> Decimal:
        return sum((r.get_horas_trabajadas() for r in self.__registros), Decimal("0"))

    def registrar_tiempo(self, empleado, id_registro, fecha, horas, descripcion):
        if not any(e is empleado for e in self.__empleados):
            raise ValueError("Se debe usar el empleado asignado a este proyecto")
        if any(r.get_id() == id_registro for r in self.__registros):
            raise ValueError("Ya existe ese registro en el proyecto")
        if any(r.get_id() == id_registro for r in empleado.listar_registros()):
            raise ValueError("Ya existe ese registro en el empleado")
        registro = RegistroTiempo(id_registro, fecha, horas, descripcion)
        empleado.agregar_registro(registro)
        self.agregar_registro(registro)
        return registro
