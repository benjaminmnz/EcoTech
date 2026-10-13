


class Departamento:

    def __init__(self, id_departamento, nombre):
        self._id = id_departamento
        self.nombre = nombre
        self._gerente = None
        self.empleados = []

    def get_id(self):
        return self._id

    def asignar_empleado(self, empleado):
        """Agrega un empleado al departamento"""
        if empleado not in self.empleados:
            self.empleados.append(empleado)
            empleado.departamento = self

    def listar_empleados(self):
        """Devuelve la lista de empleados"""
        return self.empleados
