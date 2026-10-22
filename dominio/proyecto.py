from datetime import date
from dominio.empleado import Empleado
from dominio.registro_tiempo import RegistroTiempo

class Proyecto:
    def __init__(
        self,
        id_proyecto: int,
        nombre: str,
        descripcion: str,
        fecha_inicio: date
    ):
        if not nombre.strip():
            raise ValueError("El nombre del proyecto no puede estar vacío")

        self.__id = id_proyecto
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.__empleados = []
        self.__registros = []

    def get_id(self) -> int:
        return self.__id

    def asignar_empleado(self, empleado: Empleado):
        for integrante in self.__empleados:
            if integrante.get_id() == empleado.get_id():
                raise ValueError("El empleado ya está asignado a este proyecto")
    
        self.__empleados.append(empleado)

    def listar_empleados(self) -> list:
        return self.__empleados.copy()

    def agregar_registro(self, registro: RegistroTiempo):
        for existente in self.__registros:
            if existente.get_id() == registro.get_id():
                raise ValueError("El registro ya está asociado a este proyecto")

        self.__registros.append(registro)

    def calcular_horas_totales(self) -> float:
        total = 0.0

        for registro in self.__registros:
            total += registro.get_horas_trabajadas()

        return total