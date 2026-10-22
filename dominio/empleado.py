from datetime import date
from dominio.persona import Persona
from dominio.excepciones import SalarioInvalidoError
from dominio.cuenta_usuario import CuentaUsuario
from dominio.registro_tiempo import RegistroTiempo

class Empleado(Persona):
    def __init__(
        self,
        nombre: str,
        direccion: str,
        telefono: str,
        email: str,
        id_empleado: int,
        fecha_inicio_contrato: date,
        salario: float
    ):
        super().__init__(nombre, direccion, telefono, email)

        self.__id = id_empleado
        self.fecha_inicio_contrato = fecha_inicio_contrato

        if salario <= 0:
            raise SalarioInvalidoError("El salario debe ser mayor que cero")

        self.__salario = salario

        self.__cuenta = None

        self.departamento = None

        self.__registros = []

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

    def asignar_cuenta(self, cuenta: CuentaUsuario):
        if self.__cuenta is not None:
            raise ValueError("El empleado ya tiene una cuenta asignada")

        self.__cuenta = cuenta

    def agregar_registro(self, registro: RegistroTiempo):
        if registro.empleado is not None:
            raise ValueError("El registro ya tiene un empleado asociado")

        for existente in self.__registros:
            if existente.get_id() == registro.get_id():
                raise ValueError("Ya existe un registro con ese identificador")

        self.__registros.append(registro)
        registro.empleado = self

    def listar_registros(self) -> list:
        return self.__registros.copy()