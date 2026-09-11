
from dominio import Persona


class Empleado(Persona):
    def __init__(self, id, fechaInicioContrato, salario):
        self.id = int(id)
        self.fechaInicioContrato = str(fechaInicioContrato)
        self.salario = float(salario)

    def getId():
        "Contiene la id"

    def getSalario():
        "Contiene el salario"

    def subirSalario(self, monto):
        "Bool"

    def actualizarDatosContacto(self, direccion, telefono):
        "void"

    