from datetime import date
from decimal import Decimal

from dominio.validaciones import identificador, fecha_valida, texto, decimal_positivo


class RegistroTiempo:
    def __init__(self, id_registro: int, fecha: date, horas_trabajadas, descripcion_tarea: str):
        self.__id = identificador(id_registro)
        self.fecha = fecha_valida(fecha)
        self.descripcion_tarea = texto(descripcion_tarea, "La tarea")
        self.registrar(horas_trabajadas)
        self.empleado = None
        self.proyecto = None

    def get_id(self) -> int:
        return self.__id

    def get_horas_trabajadas(self) -> Decimal:
        return self.__horas_trabajadas

    def registrar(self, horas):
        if not self.__validar_horas(horas):
            raise ValueError("Las horas deben ser positivas, no superar 24 y tener hasta dos decimales")
        self.__horas_trabajadas = decimal_positivo(horas, "Las horas", 24)

    def __validar_horas(self, horas):
        try:
            decimal_positivo(horas, "Las horas", 24)
        except ValueError:
            return False
        return True
