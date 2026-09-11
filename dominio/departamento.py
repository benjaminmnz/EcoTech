
from dominio import Empleado

class Empleado:
    """Un empleado de EcoTech. Registra su tiempo en proyectos."""

    def __init__(self, rut, nombre, fecha_ingreso, sueldo_base):
        self.rut = rut                      # texto, no número
        self.nombre = nombre
        self.fecha_ingreso = fecha_ingreso
        self.sueldo_base = sueldo_base
        self.registros = []                 # cardinalidad 1..*  ->  lista
        self.departamento = None            # cardinalidad 0..1  ->  puede ser None

    def registrar_hora(self, registro):
        """Hace algo: cambia el estado del objeto."""
        ...

    def total_horas(self):
        """Calcula y devuelve: no cambia nada."""

