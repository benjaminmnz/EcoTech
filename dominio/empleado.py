from dominio.persona import Persona


class Empleado(Persona):
    def __init__(
        self,
        nombre: str,
        direccion: str,
        telefono: str,
        email: str,
        id_empleado: int,
        fecha_inicio_contrato: str,
        salario: float
    ):
        super().__init__(nombre, direccion, telefono, email)

        self.__id = id_empleado
        self.fecha_inicio_contrato = fecha_inicio_contrato

        if salario <= 0:
            raise ValueError("El salario debe ser mayor que cero")

        self.__salario = salario

    def get_id(self) -> int:
        return self.__id

    def get_salario(self) -> float:
        return self.__salario

    def subir_salario(self, monto: float) -> bool:
        if monto <= 0:
            return False

        self.__salario += monto
        return True

    def actualizar_datos_contacto(self, direccion: str, telefono: str):
        self.direccion = direccion
        self.telefono = telefono