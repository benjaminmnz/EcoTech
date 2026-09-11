from dominio import Departamento
from dominio import Empleado
from dominio import Persona
from dominio import RegistroTiempo

def main():
    ana = Empleado(1, "11-09-2026", 700000)
    dep = Departamento(1,"Operaciones", ana)
    dep.agregar_empleado(ana)