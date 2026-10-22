from dominio.empleado import Empleado


class Departamento:
    def __init__(self, id_departamento: int, nombre: str):
        if not nombre.strip():
            raise ValueError("El nombre del departamento no puede estar vacío")

        self.__id = id_departamento
        self.nombre = nombre
        self.__gerente = None
        self.__empleados = []

    def get_id(self) -> int:
        return self.__id

    def listar_empleados(self) -> list:
        return self.__empleados.copy()

    def asignar_empleado(self, empleado: Empleado):
        if empleado.departamento is not None:
            raise ValueError("El empleado ya tiene un departamento asignado")

        self.__empleados.append(empleado)
        empleado.departamento = self

    def asignar_gerente(self, empleado: Empleado):
        if empleado.departamento is not self:
            raise ValueError("El gerente debe pertenecer a este departamento")

        self.__gerente = empleado

    def get_gerente(self):
        return self.__gerente