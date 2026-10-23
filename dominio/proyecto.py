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
        if registro.proyecto is not None:
            raise ValueError("El registro ya tiene un proyecto asociado")

        if registro.empleado is None:
            raise ValueError("El registro debe tener un empleado asociado")

        empleado_asignado = False

        for integrante in self.__empleados:
            if integrante.get_id() == registro.empleado.get_id():
                empleado_asignado = True
                break

        if not empleado_asignado:
            raise ValueError("El empleado no está asignado a este proyecto")

        for existente in self.__registros:
            if existente.get_id() == registro.get_id():
                raise ValueError("Ya existe un registro con ese identificador")

        self.__registros.append(registro)
        registro.proyecto = self

    def calcular_horas_totales(self) -> float:
        total = 0.0

        for registro in self.__registros:
            total += registro.get_horas_trabajadas()

        return total

    def registrar_tiempo(
        self,
        empleado: Empleado,
        id_registro: int,
        fecha: date,
        horas: float,
        descripcion: str
    ):
        empleado_asignado = False

        for integrante in self.__empleados:
            if integrante.get_id() == empleado.get_id():
                empleado_asignado = True
                break

        if not empleado_asignado:
            raise ValueError("El empleado no está asignado a este proyecto")

        for existente in self.__registros:
            if existente.get_id() == id_registro:
                raise ValueError("Ya existe un registro con ese identificador")

        registro = RegistroTiempo(
            id_registro=id_registro,
            fecha=fecha,
            horas_trabajadas=horas,
            descripcion_tarea=descripcion
        )

        empleado.agregar_registro(registro)
        self.agregar_registro(registro)

        return registro