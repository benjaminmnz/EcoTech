from dominio.empleado import Empleado
from dominio.validaciones import identificador, texto


class Departamento:
    def __init__(self, id_departamento: int, nombre: str):
        self.__id = identificador(id_departamento)
        self.nombre = texto(nombre, "El nombre del departamento")
        self.__gerente = None
        self.__empleados = []

    def get_id(self) -> int:
        return self.__id

    def asignar_empleado(self, empleado: Empleado):
        if not isinstance(empleado, Empleado):
            raise ValueError("Se debe entregar un empleado")
        if empleado.departamento is not None:
            raise ValueError("El empleado ya tiene un departamento")
        if any(e.get_id() == empleado.get_id() for e in self.__empleados):
            raise ValueError("El empleado ya pertenece al departamento")
        self.__empleados.append(empleado)
        empleado.departamento = self

    def listar_empleados(self) -> list:
        return self.__empleados.copy()

    def asignar_gerente(self, empleado: Empleado):
        if empleado.departamento is not self:
            raise ValueError("El gerente debe pertenecer al departamento")
        self.__gerente = empleado

    def get_gerente(self):
        return self.__gerente
