
from dominio.persona import Persona


class Empleado(Persona):

    def __init__(self, nombre, direccion, telefono, email, id_empleado, fecha_inicio_contrato, salario):
        super().__init__(nombre, direccion, telefono, email)  # parte heredada
        self._id = id_empleado
        self.fecha_inicio_contrato = fecha_inicio_contrato
        self._salario = salario
        self.registros = []
        self.departamento = None

    def get_id(self):
        """Muestra el id"""
        return self._id

    def get_salario(self):
        """Muestra el salario"""
        return self._salario

    def subir_salario(self, monto):
        """Sube el salario y devuelve True si se pudo"""
        if monto <= 0:
            return False
        self._salario += monto
        return True

    def actualizar_datos_contacto(self, direccion, telefono):
        """Actualiza la direccion y el telefono"""
        self.direccion = direccion
        self.telefono = telefono

