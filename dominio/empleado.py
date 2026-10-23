from datetime import date
from decimal import Decimal

from dominio.persona import Persona
from dominio.cuenta_usuario import CuentaUsuario
from dominio.registro_tiempo import RegistroTiempo
from dominio.excepciones import SalarioInvalidoError
from dominio.validaciones import identificador, fecha_valida, decimal_positivo, texto


class Empleado(Persona):
    def __init__(self, nombre: str, direccion: str, telefono: str, email: str,
                 id_empleado: int, fecha_inicio_contrato: date, salario):
        super().__init__(nombre, direccion, telefono, email)
        self.__id = identificador(id_empleado)
        self.fecha_inicio_contrato = fecha_valida(fecha_inicio_contrato)
        try:
            self.__salario = decimal_positivo(salario, "El salario", "9999999999.99")
        except ValueError as error:
            raise SalarioInvalidoError(str(error)) from error
        self.__cuenta = None
        self.departamento = None
        self.__registros = []

    def get_id(self) -> int:
        return self.__id

    def get_salario(self) -> Decimal:
        return self.__salario

    def subir_salario(self, monto) -> bool:
        try:
            aumento = decimal_positivo(monto, "El aumento", "9999999999.99")
            nuevo = decimal_positivo(self.__salario + aumento, "El salario", "9999999999.99")
        except ValueError:
            return False
        self.__salario = nuevo
        return True

    def actualizar_datos_contacto(self, direccion: str, telefono: str):
        # Validar ambos datos antes de modificar cualquiera.
        direccion = texto(direccion, "La dirección")
        telefono = texto(telefono, "El teléfono")
        self.direccion = direccion
        self.telefono = telefono

    def asignar_cuenta(self, cuenta: CuentaUsuario):
        if not isinstance(cuenta, CuentaUsuario):
            raise ValueError("Se debe entregar una cuenta")
        if self.__cuenta is not None or cuenta.empleado is not None:
            raise ValueError("El empleado o la cuenta ya tienen una asociación")
        self.__cuenta = cuenta
        cuenta.empleado = self

    def get_cuenta(self):
        return self.__cuenta

    def agregar_registro(self, registro: RegistroTiempo):
        if not isinstance(registro, RegistroTiempo):
            raise ValueError("Se debe entregar un registro de tiempo")
        if registro.empleado is not None:
            raise ValueError("El registro ya tiene un empleado asociado")
        if any(existente.get_id() == registro.get_id() for existente in self.__registros):
            raise ValueError("Ya existe un registro con ese identificador")
        self.__registros.append(registro)
        registro.empleado = self

    def listar_registros(self) -> list:
        return self.__registros.copy()
